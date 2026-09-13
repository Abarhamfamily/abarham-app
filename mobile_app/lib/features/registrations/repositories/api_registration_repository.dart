import 'dart:convert';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/api_client.dart';
import '../models/registration_create_response.dart';
import 'registration_repository.dart';

class ApiRegistrationRepository implements RegistrationRepository {
  final ApiClient _apiClient;

  ApiRegistrationRepository({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  @override
  Future<RegistrationCreateResponse> createRegistration({
    required String tripId,
    required int passengerCount,
    String? vehicleType,
    int emptySeatsProvided = 0,
    String? notes,
  }) async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/registrations');
    final response = await _apiClient.authenticatedPost(
      url,
      body: jsonEncode({
        'trip_id': tripId,
        'passenger_count': passengerCount,
        'vehicle_type': vehicleType,
        'empty_seats_provided': emptySeatsProvided,
        'notes': notes,
      }),
    );

    switch (response.statusCode) {
      case 201:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return RegistrationCreateResponse.fromJson(data);
      case 400:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(data['detail'] as String? ?? 'کیف پول یافت نشد');
      case 402:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(data['detail'] as String? ?? 'موجودی کیف پول کافی نیست');
      case 404:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(data['detail'] as String? ?? 'تور یافت نشد');
      case 409:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(data['detail'] as String? ?? 'شما قبلاً برای این تور اقدام کرده‌اید');
      case 422:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(data['detail'] as String? ?? 'اطلاعات ارسالی نامعتبر است');
      default:
        throw Exception('خطا در ارتباط با سرور');
    }
  }
}