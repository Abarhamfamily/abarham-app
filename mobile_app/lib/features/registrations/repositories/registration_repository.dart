import '../models/registration_create_response.dart';

abstract class RegistrationRepository {
  Future<RegistrationCreateResponse> createRegistration({
    required String tripId,
    required int passengerCount,
    String? vehicleType,
    int emptySeatsProvided,
    String? notes,
  });
}