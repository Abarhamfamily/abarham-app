// Tests for ApiAuthRepository login method using mocktail.

import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:http/http.dart' as http;

import 'package:mobile_app/features/auth/repositories/api_auth_repository.dart';
import 'package:mobile_app/features/auth/models/token_response.dart';
import 'package:mobile_app/core/storage/auth_token_storage.dart';

class MockHttpClient extends Mock implements http.Client {}

class MockAuthTokenStorage extends Mock implements AuthTokenStorage {}

void main() {
  setUpAll(() {
    registerFallbackValue(Uri());
    registerFallbackValue(<String, String>{});
  });
  late MockHttpClient mockClient;
  late MockAuthTokenStorage mockStorage;
  late ApiAuthRepository repository;

  setUp(() {
    mockClient = MockHttpClient();
    mockStorage = MockAuthTokenStorage();
    // Stub saveTokens to avoid MissingStub errors
    when(() => mockStorage.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        )).thenAnswer((_) async {});
    repository = ApiAuthRepository(tokenStorage: mockStorage, client: mockClient);
  });

  const fakePhone = '09121234567';
  const fakePassword = 'password123';
  const fakeAccessToken = 'fake_access_token';
  const fakeRefreshToken = 'fake_refresh_token';

  final successJson = jsonEncode({
    'access_token': fakeAccessToken,
    'refresh_token': fakeRefreshToken,
    'user': {
      'id': 'user123',
      'phone_number': fakePhone,
      'full_name': 'John Doe',
      'email': 'john@example.com',
      'national_id': '1234567890',
      'is_active': true,
    },
  });

  test('login returns TokenResponse on 200 and saves tokens', () async {
    // Arrange
    when(() => mockClient.post(
          any<Uri>(that: isA<Uri>()),
          headers: any(named: 'headers'),
          body: any(named: 'body'),
        )).thenAnswer((_) async => http.Response(successJson, 200));

    // Act
    final result = await repository.login(fakePhone, fakePassword);

    // Assert
    expect(result, isA<TokenResponse>());
    expect(result.accessToken, fakeAccessToken);
    expect(result.refreshToken, fakeRefreshToken);
    expect(result.user.id, 'user123');
    verify(() => mockStorage.saveTokens(
          accessToken: fakeAccessToken,
          refreshToken: fakeRefreshToken,
        )).called(1);
  });

  test('login throws Exception with message for 401', () async {
    when(() => mockClient.post(
          any(that: isA<Uri>()),
          headers: any(named: 'headers'),
          body: any(named: 'body'),
        ))
        .thenAnswer((_) async => http.Response('', 401));

    expect(
        () => repository.login(fakePhone, fakePassword),
        throwsA(predicate((e) => e is Exception && e.toString().contains('شماره تماس یا رمز عبور اشتباه است'))));
    verifyNever(() => mockStorage.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ));
  });

  test('login throws Exception with message for 403', () async {
    when(() => mockClient.post(
          any(that: isA<Uri>()),
          headers: any(named: 'headers'),
          body: any(named: 'body'),
        ))
        .thenAnswer((_) async => http.Response('', 403));

    expect(
        () => repository.login(fakePhone, fakePassword),
        throwsA(predicate((e) => e is Exception && e.toString().contains('حساب کاربری هنوز فعال نشده است'))));
    verifyNever(() => mockStorage.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ));
  });

  test('login throws Exception with message for 422', () async {
    when(() => mockClient.post(
          any(that: isA<Uri>()),
          headers: any(named: 'headers'),
          body: any(named: 'body'),
        ))
        .thenAnswer((_) async => http.Response('', 422));

    expect(
        () => repository.login(fakePhone, fakePassword),
        throwsA(predicate((e) => e is Exception && e.toString().contains('اطلاعات واردشده معتبر نیست'))));
    verifyNever(() => mockStorage.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ));
  });
}
