import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/router/app_router.dart';
import '../models/trip.dart';
import '../repositories/api_trip_repository.dart';
import '../repositories/trip_repository.dart';
import '../../trips/pages/trip_details_page.dart';
import '../../trips/pages/trips_page.dart';
import '../../auth/repositories/api_auth_repository.dart';
import '../../auth/pages/login_page.dart';
import '../../registrations/pages/my_registrations_page.dart';
import '../../wallet/pages/wallet_page.dart';
import '../../profile/pages/profile_page.dart';


part '../widgets/header.dart';
part '../widgets/small_button.dart';
part '../widgets/hero_card.dart';
part '../widgets/featured_trip.dart';
part '../widgets/section_title.dart';
part '../widgets/categories.dart';
part '../widgets/trip_card.dart';
part '../widgets/community_card.dart';
part '../widgets/nav_item.dart';
part '../widgets/bottom_navigation.dart';

class HomePage extends StatefulWidget {
  final TripRepository _tripRepository;

  HomePage({super.key, TripRepository? repository})
      : _tripRepository = repository ?? ApiTripRepository();

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Trip>> _tripsFuture;

  @override
  void initState() {
    super.initState();
    _tripsFuture = widget._tripRepository.getTrips();
  }

  void _retry() {
    setState(() {
      _tripsFuture = widget._tripRepository.getTrips();
    });
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Trip>>(
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
                const Text('دریافت اطلاعات با خطا مواجه شد'),
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

        final featuredTrip = trips[0];
        final secondTrip = trips.length > 1 ? trips[1] : featuredTrip;

        return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: SafeArea(
          child: CustomScrollView(
            slivers: [
              SliverToBoxAdapter(
                 child: _Header(
                  onLogout: () async {
                    await ApiAuthRepository().logout();
                    if (context.mounted) {
                      Navigator.of(context).pushAndRemoveUntil(
                        AppRouter.route(builder: (_) => LoginPage()),
                        (route) => false,
                      );
                    }
                  },
                  onMyRegistrations: () {
                    Navigator.of(context).push(
                      AppRouter.route(builder: (_) => const MyRegistrationsPage()),
                    );
                  },
                ),
               ),
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    _HeroCard(),
                    const SizedBox(height: 24),
                    _SectionTitle(
                      title: 'دسته‌بندی سفرها',
                      action: 'مشاهده همه',
                    ),
                    const SizedBox(height: 12),
                    _Categories(),
                    const SizedBox(height: 28),
                    _SectionTitle(
                      title: 'تور ویژه',
                      action: 'مشاهده همه',
                    ),
                    const SizedBox(height: 12),
                    _FeaturedTrip(
                      trip: featuredTrip,
                      image:
                          'https://images.unsplash.com/photo-1551632811-561732d1e306?w=900&h=500&fit=crop',
                    ),
                    const SizedBox(height: 28),
                    GestureDetector(
                      onTap: () {
                        Navigator.of(context).push(
                          AppRouter.route(
                            builder: (_) => TripsPage(),
                          ),
                        );
                      },
                      child: _SectionTitle(
                        title: 'تورهای برگزیده',
                        action: 'همه تورها',
                      ),
                    ),
                    const SizedBox(height: 12),
                    _TripCard(
                      image:
                          'https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&h=500&fit=crop',
                      trip: featuredTrip,
                    ),
                    const SizedBox(height: 14),
                    _TripCard(
                      image:
                          'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=500&fit=crop',
                      trip: secondTrip,
                    ),
                    const SizedBox(height: 28),
                    _CommunityCard(),
                  ]),
                ),
              ),
            ],
          ),
        ),
        bottomNavigationBar: const _BottomNavigation(),
      ),
        );
      },
    );
  }
}
