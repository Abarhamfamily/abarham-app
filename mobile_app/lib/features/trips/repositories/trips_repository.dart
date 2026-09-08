import '../../home/models/trip.dart';
import '../../home/repositories/api_trip_repository.dart';
import '../../home/repositories/trip_repository.dart';

class TripsRepository implements TripRepository {
  final TripRepository _repository;

  TripsRepository({TripRepository? repository})
      : _repository = repository ?? ApiTripRepository();

  @override
  Future<List<Trip>> getTrips() {
    return _repository.getTrips();
  }
}
