import '../models/trip.dart';

abstract interface class TripRepository {
  Future<List<Trip>> getTrips();
}
