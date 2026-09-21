import '../models/token_response.dart';

abstract class AuthRepository {
  Future<TokenResponse> login(String phoneNumber, String password);
  Future<void> logout();
  Future<Map<String, dynamic>> register({
    required String phoneNumber,
    required String fullName,
    required String password,
  });
  Future<TokenResponse> verifyOtp({
    required String phoneNumber,
    required String otp,
  });
}