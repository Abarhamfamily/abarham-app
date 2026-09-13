import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../home/models/trip.dart';
import '../../registrations/repositories/api_registration_repository.dart';

class TripDetailsPage extends StatefulWidget {
  final Trip trip;

  const TripDetailsPage({
    super.key,
    required this.trip,
  });

  @override
  State<TripDetailsPage> createState() => _TripDetailsPageState();
}

class _TripDetailsPageState extends State<TripDetailsPage> {
  bool _isRegistering = false;

  Trip get trip => widget.trip;

  bool get _hasDescription =>
      trip.description != null && trip.description!.trim().isNotEmpty;

  Future<void> _handleRegisterPressed() async {
    final vehicleType = await showDialog<String>(
      context: context,
      builder: (context) => _VehicleTypeDialog(),
    );

    if (vehicleType == null) return;
    if (!mounted) return;

    setState(() => _isRegistering = true);

    final repository = ApiRegistrationRepository();
    try {
      final result = await repository.createRegistration(
        tripId: trip.id,
        passengerCount: 1,
        vehicleType: vehicleType,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result.message)),
      );
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() => _isRegistering = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('جزئیات سفر'),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildHeaderCard(),
              const SizedBox(height: 16),
              _buildInfoCard(),
              if (_hasDescription) ...[
                const SizedBox(height: 16),
                _buildDescriptionCard(),
              ],
              const SizedBox(height: 16),
              _buildRegisterButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRegisterButton() {
    return ElevatedButton(
      onPressed: _isRegistering ? null : _handleRegisterPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      child: _isRegistering
          ? const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(
                color: Colors.white,
                strokeWidth: 2,
              ),
            )
          : const Text(
              'ثبت‌نام در این تور',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
            ),
    );
  }

  Widget _buildHeaderCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE5E4DC)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                  trip.title,
                  style: const TextStyle(
                    color: AppColors.foreground,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              if (trip.difficultyLevel != null &&
                  trip.difficultyLevel!.trim().isNotEmpty) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: .1),
                    borderRadius: BorderRadius.circular(9),
                  ),
                  child: Text(
                    trip.difficultyLevel!,
                    style: const TextStyle(
                      color: AppColors.primary,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(
                Icons.location_on_outlined,
                size: 17,
                color: AppColors.primary,
              ),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  trip.destination,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF718078),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard() {
    final rows = <_InfoRow>[
      _InfoRow(label: 'تاریخ شروع', value: _formatDate(trip.startDate)),
      _InfoRow(label: 'تاریخ پایان', value: _formatDate(trip.endDate)),
      _InfoRow(label: 'قیمت', value: _formatPrice(trip.price)),
      _InfoRow(label: 'پیش‌پرداخت', value: _formatPrice(trip.depositAmount)),
      _InfoRow(
        label: 'ظرفیت کل',
        value: '${_toPersianDigits(trip.capacity.toString())} نفر',
      ),
      _InfoRow(
        label: 'ظرفیت باقی‌مانده',
        value: '${_toPersianDigits(trip.remainingCapacity.toString())} نفر',
      ),
      _InfoRow(label: 'وضعیت', value: trip.status),
      _InfoRow(label: 'سطح دشواری', value: trip.difficultyLevel ?? '-'),
      _InfoRow(label: 'وسیله حمل‌ونقل', value: trip.transportationType ?? '-'),
      _InfoRow(label: 'نقطه حرکت', value: trip.meetingPoint ?? '-'),
      _InfoRow(label: 'ساعت حرکت', value: trip.departureTime ?? '-'),
    ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE5E4DC)),
      ),
      child: Column(
        children: [
          for (var i = 0; i < rows.length; i++) ...[
            if (i > 0) const Divider(height: 1, color: Color(0xFFE5E4DC)),
            rows[i],
          ],
        ],
      ),
    );
  }

  Widget _buildDescriptionCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE5E4DC)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'توضیحات',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.bold,
              color: AppColors.foreground,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            trip.description!,
            style: const TextStyle(
              fontSize: 13,
              height: 1.8,
              color: Color(0xFF718078),
            ),
          ),
        ],
      ),
    );
  }
}

class _VehicleTypeDialog extends StatefulWidget {
  @override
  State<_VehicleTypeDialog> createState() => _VehicleTypeDialogState();
}

class _VehicleTypeDialogState extends State<_VehicleTypeDialog> {
  String _selected = 'own';

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('نوع وسیله نقلیه'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          RadioListTile<String>(
            title: const Text('با ماشین شخصی خودم'),
            value: 'own',
            groupValue: _selected,
            onChanged: (value) => setState(() => _selected = value!),
          ),
          RadioListTile<String>(
            title: const Text('با ماشین سایر اعضا'),
            value: 'other',
            groupValue: _selected,
            onChanged: (value) => setState(() => _selected = value!),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('انصراف'),
        ),
        ElevatedButton(
          onPressed: () => Navigator.of(context).pop(_selected),
          child: const Text('ثبت‌نام'),
        ),
      ],
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 13,
              color: Color(0xFF718078),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.end,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: AppColors.foreground,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

String _toPersianDigits(String input) {
  const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
  return input.split('').map((character) {
    final digit = int.tryParse(character);
    return digit == null ? character : persianDigits[digit];
  }).join();
}

String _formatDate(DateTime date) {
  final month = date.month.toString().padLeft(2, '0');
  final day = date.day.toString().padLeft(2, '0');
  return _toPersianDigits('${date.year}/$month/$day');
}

String _formatPrice(String rawPrice) {
  final integerPart = rawPrice.split('.').first;
  final groups = <String>[];
  var end = integerPart.length;

  while (end > 0) {
    final start = end > 3 ? end - 3 : 0;
    groups.insert(0, integerPart.substring(start, end));
    end = start;
  }

  return '${_toPersianDigits(groups.join(','))} تومان';
}