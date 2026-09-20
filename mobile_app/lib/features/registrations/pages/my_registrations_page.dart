import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../models/registration_with_trip.dart';
import '../repositories/api_registration_repository.dart';

class MyRegistrationsPage extends StatefulWidget {
  const MyRegistrationsPage({super.key});

  @override
  State<MyRegistrationsPage> createState() => _MyRegistrationsPageState();
}

class _MyRegistrationsPageState extends State<MyRegistrationsPage> {
  final ApiRegistrationRepository _repository = ApiRegistrationRepository();
  late Future<List<RegistrationWithTrip>> _future;
  String? _cancellingId;
  String? _payingId;

  @override
  void initState() {
    super.initState();
    _future = _repository.getMyRegistrations();
  }

  void _retry() {
    setState(() {
      _future = _repository.getMyRegistrations();
    });
  }

  static const Map<String, String> _statusLabels = {
    'pending_payment': 'در انتظار پرداخت',
    'confirmed': 'تأیید شده',
    'cancelled': 'لغو شده',
    'completed': 'انجام شده',
    'expired': 'منقضی شده',
  };

  static const Map<String, String> _vehicleLabels = {
    'own': 'با ماشین شخصی',
    'other': 'با ماشین سایر اعضا',
  };

  static const Set<String> _cancellableStatuses = {
    'pending_payment',
    'confirmed',
  };

  String _formatPrice(String rawPrice) {
    final integerPart = rawPrice.split('.').first;
    final groups = <String>[];
    var end = integerPart.length;
    while (end > 0) {
      final start = end > 3 ? end - 3 : 0;
      groups.insert(0, integerPart.substring(start, end));
      end = start;
    }
    return '${groups.join(',')} تومان';
  }

  bool _hasRemainingBalance(RegistrationWithTrip reg) {
    final value = double.tryParse(reg.remainingAmount) ?? 0;
    return value > 0;
  }

  Future<void> _handleCancelPressed(RegistrationWithTrip reg) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('لغو ثبت‌نام'),
          content: Text(
            'آیا از لغو ثبت‌نام تور «${reg.tripTitle}» مطمئن هستید؟ مبلغ پرداختی به کیف پول شما بازگردانده می‌شود.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('انصراف'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('لغو ثبت‌نام'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) return;
    if (!mounted) return;

    setState(() => _cancellingId = reg.id);

    try {
      final message = await _repository.cancelRegistration(reg.id);
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );

      setState(() {
        _future = _repository.getMyRegistrations();
      });
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() => _cancellingId = null);
      }
    }
  }

  Future<void> _handlePayRemainingPressed(RegistrationWithTrip reg) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('پرداخت باقی‌مانده'),
          content: Text(
            'مبلغ ${_formatPrice(reg.remainingAmount)} از کیف پول شما برای تور «${reg.tripTitle}» کسر می‌شود. ادامه می‌دهید؟',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('انصراف'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('پرداخت'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) return;
    if (!mounted) return;

    setState(() => _payingId = reg.id);

    try {
      final result = await _repository.payRemainingAmount(
        registrationId: reg.id,
        amount: reg.remainingAmount,
      );
      if (!mounted) return;

      final message = result.status == 'already_processed'
          ? 'این پرداخت قبلاً پردازش شده است'
          : 'پرداخت با موفقیت انجام شد';

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );

      setState(() {
        _future = _repository.getMyRegistrations();
      });
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() => _payingId = null);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('سفرهای من'),
        ),
        body: FutureBuilder<List<RegistrationWithTrip>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('دریافت سفرها با خطا مواجه شد'),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _retry,
                      child: const Text('تلاش مجدد'),
                    ),
                  ],
                ),
              );
            }

            final registrations = snapshot.data ?? const <RegistrationWithTrip>[];
            if (registrations.isEmpty) {
              return const Center(
                child: Text('هنوز در هیچ توری ثبت‌نام نکرده‌اید'),
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: registrations.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final reg = registrations[index];
                final isCancellable = _cancellableStatuses.contains(reg.status);
                final isCancelling = _cancellingId == reg.id;
                final canPayRemaining = isCancellable && _hasRemainingBalance(reg);
                final isPaying = _payingId == reg.id;

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
                      Text(
                        reg.tripTitle,
                        style: const TextStyle(
                          color: AppColors.foreground,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        reg.tripDestination,
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF718078),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            _statusLabels[reg.status] ?? reg.status,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: AppColors.primary,
                            ),
                          ),
                          Text(
                            _formatPrice(reg.totalPrice),
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: AppColors.foreground,
                            ),
                          ),
                        ],
                      ),
                      if (reg.vehicleType != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          _vehicleLabels[reg.vehicleType] ?? reg.vehicleType!,
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFF718078),
                          ),
                        ),
                      ],
                      if (canPayRemaining) ...[
                        const SizedBox(height: 8),
                        Text(
                          'باقی‌مانده: ${_formatPrice(reg.remainingAmount)}',
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.orange,
                          ),
                        ),
                      ],
                      if (canPayRemaining) ...[
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: isPaying ? null : () => _handlePayRemainingPressed(reg),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.primary,
                              foregroundColor: Colors.white,
                            ),
                            child: isPaying
                                ? const SizedBox(
                                    height: 16,
                                    width: 16,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.white,
                                    ),
                                  )
                                : const Text('پرداخت باقی‌مانده'),
                          ),
                        ),
                      ],
                      if (isCancellable) ...[
                        const SizedBox(height: 8),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton(
                            onPressed: isCancelling ? null : () => _handleCancelPressed(reg),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.red,
                              side: const BorderSide(color: Colors.red),
                            ),
                            child: isCancelling
                                ? const SizedBox(
                                    height: 16,
                                    width: 16,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                : const Text('لغو ثبت‌نام'),
                          ),
                        ),
                      ],
                    ],
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}