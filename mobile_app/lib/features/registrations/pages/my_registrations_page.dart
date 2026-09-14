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
  late Future<List<RegistrationWithTrip>> _future;

  @override
  void initState() {
    super.initState();
    _future = ApiRegistrationRepository().getMyRegistrations();
  }

  void _retry() {
    setState(() {
      _future = ApiRegistrationRepository().getMyRegistrations();
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