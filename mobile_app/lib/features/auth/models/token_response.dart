import 'user.dart';

class TokenResponse {
  final String accessToken;
  final String refreshToken;
  final User user;

  TokenResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.user,
  });
}