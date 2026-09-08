import 'trip.dart';

class HomeTripMockData {
  static final Trip chakroudTrip = Trip(
    id: 'home-chakroud-001',
    title: 'ماجراجویی در دره چاکرود',
    destination: 'چاکرود، مازندران',
    description: null,
    startDate: DateTime(2026, 8, 21),
    endDate: DateTime(2026, 8, 23),
    price: '2800000',
    depositAmount: '1000000',
    capacity: 15,
    remainingCapacity: 4,
    status: 'published',
    transportationType: null,
    difficultyLevel: 'متوسط',
    meetingPoint: null,
    departureTime: null,
  );

  static final Trip mazandaranForestTrip = Trip(
    id: 'home-mazandaran-forest-001',
    title: 'کمپینگ در جنگل‌های مازندران',
    destination: 'جنگل‌های مازندران',
    description: null,
    startDate: DateTime(2026, 9, 12),
    endDate: DateTime(2026, 9, 13),
    price: '1800000',
    depositAmount: '700000',
    capacity: 20,
    remainingCapacity: 8,
    status: 'published',
    transportationType: null,
    difficultyLevel: 'آسان',
    meetingPoint: null,
    departureTime: null,
  );

  static final List<Trip> homeTrips = [
    chakroudTrip,
    mazandaranForestTrip,
  ];
}
