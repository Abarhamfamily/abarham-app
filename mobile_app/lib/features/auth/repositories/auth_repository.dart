import '../models/token_response.dart';

abstract class AuthRepository {
  Future<TokenResponse> login(String phoneNumber, String password);
}