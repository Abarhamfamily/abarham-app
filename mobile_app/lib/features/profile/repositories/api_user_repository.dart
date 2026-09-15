import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/constants/api_constants.dart';
import '../../../core/storage/auth_token_storage.dart';
import '../models/user_profile.dart';
import 'user_repository.dart';

class ApiUserRepository implements UserRepository {
  final http.Client _client;
  final AuthTokenStorage _tokenStorage;

  ApiUserRepository({http.Client? client, AuthTokenStorage? tokenStorage})
      : _client = client ?? http.Client(),
        _tokenStorage = tokenStorage ?? AuthTokenStorage();

  Future<Map<String, String>> _authHeaders() async {
    final token = await _tokenStorage.getAccessToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  @override
  Future<UserWithProfile> getMyProfile() async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/users/me');
    final response = await _client.get(url, headers: await _authHeaders());

    if (response.statusCode != 200) {
      throw Exception('خطا در دریافت اطلاعات پروفایل');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return UserWithProfile.fromJson(data);
  }

  @override
  Future<UserProfileData> updateProfile({
    String? birthDate,
    String? emergencyContactName,
    String? emergencyContactPhone,
    String? medicalNotes,
    bool? vehicleHasCapacity,
    int? emptySeats,
  }) async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/users/me/profile');
    final body = <String, dynamic>{};
    if (birthDate != null) body['birth_date'] = birthDate;
    if (emergencyContactName != null) body['emergency_contact_name'] = emergencyContactName;
    if (emergencyContactPhone != null) body['emergency_contact_phone'] = emergencyContactPhone;
    if (medicalNotes != null) body['medical_notes'] = medicalNotes;
    if (vehicleHasCapacity != null) body['vehicle_has_capacity'] = vehicleHasCapacity;
    if (emptySeats != null) body['empty_seats'] = emptySeats;

    final request = http.Request('PATCH', url);
    request.headers.addAll(await _authHeaders());
    request.body = jsonEncode(body);

    final streamedResponse = await _client.send(request);
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(data['detail'] as String? ?? 'خطا در به‌روزرسانی پروفایل');
    }

    return UserProfileData.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<UserProfileData> uploadProfileImage(String filePath) async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/users/me/profile/image');
    final token = await _tokenStorage.getAccessToken();

    final request = http.MultipartRequest('POST', url);
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('file', filePath));

    final streamedResponse = await _client.send(request);
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(data['detail'] as String? ?? 'خطا در آپلود عکس');
    }

    return UserProfileData.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}