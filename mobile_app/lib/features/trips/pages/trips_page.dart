import 'package:flutter/material.dart';

import '../../../core/router/app_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../home/models/trip.dart';
import '../repositories/trips_repository.dart';
import 'trip_details_page.dart';

class TripsPage extends StatefulWidget {
  final TripsRepository _repository;

  TripsPage({super.key, TripsRepository? repository})
      : _repository = repository ?? TripsRepository();

  @override
  State<TripsPage> createState() => _TripsPageState();
}

class _TripsPageState extends State<TripsPage> {
  late Future<List<Trip>> _tripsFuture;

  @override
  void initState() {
    super.initState();
    _tripsFuture = widget._repository.getTrips();
  }

  void _retry() {
    setState(() {
      _tripsFuture = widget._repository.getTrips();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('سفرها'),
      ),
      body: FutureBuilder<List<Trip>>(
        future: _tripsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(
              child: CircularProgressIndicator(),
            );
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

          final trips = snapshot.data ?? const <Trip>[];
          if (trips.isEmpty) {
            return const Center(
              child: Text('هیچ سفری یافت نشد'),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: trips.length,
            separatorBuilder: (_, __) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final trip = trips[index];

              return ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: InkWell(
                  onTap: () {
                    Navigator.of(context).push(
                      AppRouter.route(
                        builder: (_) => TripDetailsPage(trip: trip),
                      ),
                    );
                  },
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: const Color(0xFFE5E4DC),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          trip.title,
                          style: const TextStyle(
                            color: AppColors.foreground,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(trip.destination),
                        const SizedBox(height: 8),
                        Text('قیمت: ${trip.price}'),
                        const SizedBox(height: 8),
                        Text('سطح دشواری: ${trip.difficultyLevel ?? '-'}'),
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}