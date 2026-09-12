import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/token_response.dart';
import '../models/user.dart';
import '../../../core/constants/api_constants.dart';
import '../repositories/auth_repository.dart';
import '../../../core/storage/auth_token_storage.dart';
import '../../../core/network/api_client.dart';

class ApiAuthRepository implements AuthRepository {
  final ApiClient _apiClient;
  final AuthTokenStorage _tokenStorage;
  final http.Client _client;

  ApiAuthRepository({
    AuthTokenStorage? tokenStorage,
    http.Client? client,
    ApiClient? apiClient,
  })  : _tokenStorage = tokenStorage ?? AuthTokenStorage(),
        _client = client ?? http.Client(),
        _apiClient = apiClient ?? ApiClient();

  @override
  Future<TokenResponse> login(String phoneNumber, String password) async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/auth/login');
    final response = await _client.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'phone_number': phoneNumber, 'password': password}),
    );

    switch (response.statusCode) {
      case 200:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final userData = data['user'] as Map<String, dynamic>;
        final user = User(
          id: userData['id'] as String,
          phoneNumber: userData['phone_number'] as String,
          fullName: userData['full_name'] as String,
          email: userData['email'] as String?,
          nationalId: userData['national_id'] as String?,
          isActive: userData['is_active'] as bool,
        );
        final tokenResponse = TokenResponse(
          accessToken: data['access_token'] as String,
          refreshToken: data['refresh_token'] as String,
          user: user,
        );
        await _tokenStorage.saveTokens(
          accessToken: tokenResponse.accessToken,
          refreshToken: tokenResponse.refreshToken,
        );
        return tokenResponse;
      case 401:
        throw Exception('شماره تماس یا رمز عبور اشتباه است');
      case 403:
        throw Exception('حساب کاربری هنوز فعال نشده است');
      case 422:
        throw Exception('اطلاعات واردشده معتبر نیست');
      default:
        throw Exception('خطا در ارتباط با سرور');
    }
  }

  @override
  Future<void> logout() async {
    try {
      final logoutUrl = Uri.parse('${ApiConstants.baseUrl}/api/v1/auth/logout');
      await _apiClient.authenticatedPost(
        logoutUrl,
        body: jsonEncode(<String, dynamic>{}),
      );
    } catch (_) {
      // Logout is best-effort: ignore HTTP/network errors.
    }
    await _tokenStorage.clearTokens();
  }
}