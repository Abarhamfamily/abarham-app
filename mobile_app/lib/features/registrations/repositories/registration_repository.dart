import '../models/registration_create_response.dart';
import '../models/registration_with_trip.dart';

abstract class RegistrationRepository {
  Future<RegistrationCreateResponse> createRegistration({
    required String tripId,
    required int passengerCount,
    String? vehicleType,
    int emptySeatsProvided,
    String? notes,
  });

  Future<List<RegistrationWithTrip>> getMyRegistrations();

  Future<String> cancelRegistration(String registrationId);
}