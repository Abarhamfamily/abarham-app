import 'dart:convert';

import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';
import '../storage/auth_token_storage.dart';

/// Wrapper that automatically adds an Authorization header and retries the
/// request after a successful token refresh when the server returns 401.
class ApiClient {
  final http.Client _client;
  final AuthTokenStorage _tokenStorage;
  final String _baseUrl;

  ApiClient({
    http.Client? client,
    AuthTokenStorage? tokenStorage,
  })  : _client = client ?? http.Client(),
        _tokenStorage = tokenStorage ?? AuthTokenStorage(),
        _baseUrl = ApiConstants.baseUrl;

  /// Core method that performs the request, handles 401, refreshes the token
  /// and retries once if a new access token is obtained.
  Future<http.Response> _executeWithAuth(String method, Uri url,
      {Object? body}) async {
    // 1️⃣ Read current access token
    final String? accessToken = await _tokenStorage.getAccessToken();
    if (accessToken == null) {
      throw StateError(
          'Access token is null – make sure you called `saveTokens` first.');
    }
    final Map<String, String> headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    };

    // 2️⃣ Perform the HTTP request
    http.Response response;
    if (method.toUpperCase() == 'GET') {
      response = await _client.get(url, headers: headers);
    } else if (method.toUpperCase() == 'POST') {
      response = await _client.post(url, headers: headers, body: body);
    } else {
      throw UnsupportedError('Unsupported HTTP method: $method');
    }

    // 3️⃣ If we got 401, try to refresh the token
    if (response.statusCode == 401) {
      final String? refreshToken = await _tokenStorage.getRefreshToken();
      if (refreshToken == null) {
        // No refresh token – give up
        return response;
      }

      final Uri refreshUri = Uri.parse('$_baseUrl/api/v1/auth/refresh');
      final http.Response refreshResponse = await _client.post(
        refreshUri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh_token': refreshToken}),
      );

      if (refreshResponse.statusCode == 200) {
        // Refresh succeeded – store the new access token only
        final Map<String, dynamic> data = jsonDecode(refreshResponse.body);
        final String newAccessToken = data['access_token'] as String;
        await _tokenStorage.updateAccessToken(accessToken: newAccessToken);

        // Retry original request with new token
        final Map<String, String> retryHeaders = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $newAccessToken',
        };
        if (method.toUpperCase() == 'GET') {
          response = await _client.get(url, headers: retryHeaders);
        } else {
          response = await _client.post(url, headers: retryHeaders, body: body);
        }
      } else {
        // Refresh failed – clear stored tokens
        await _tokenStorage.clearTokens();
        return response;
      }
    }

    return response;
  }

  /// Public wrapper for GET requests.
  Future<http.Response> authenticatedGet(Uri url) async {
    return await _executeWithAuth('GET', url);
  }

  /// Public wrapper for POST requests.
  Future<http.Response> authenticatedPost(
    Uri url, {
    Object? body,
  }) async {
    return await _executeWithAuth('POST', url, body: body);
  }
}
