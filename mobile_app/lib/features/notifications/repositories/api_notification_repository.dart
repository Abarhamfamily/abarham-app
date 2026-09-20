import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/constants/api_constants.dart';
import '../../../core/network/api_client.dart';
import '../../../core/storage/auth_token_storage.dart';
import '../models/app_notification.dart';
import 'notification_repository.dart';

class ApiNotificationRepository implements NotificationRepository {
  final ApiClient _apiClient;
  final AuthTokenStorage _tokenStorage;

  ApiNotificationRepository({
    ApiClient? apiClient,
    AuthTokenStorage? tokenStorage,
  })  : _apiClient = apiClient ?? ApiClient(),
        _tokenStorage = tokenStorage ?? AuthTokenStorage();

  Future<Map<String, String>> _authHeaders() async {
    final token = await _tokenStorage.getAccessToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  @override
  Future<List<AppNotification>> getNotifications({bool? read}) async {
    final queryParams = <String, String>{};
    if (read != null) {
      queryParams['read'] = read.toString();
    }
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/notifications')
        .replace(queryParameters: queryParams.isEmpty ? null : queryParams);

    final response = await _apiClient.authenticatedGet(url);

    switch (response.statusCode) {
      case 200:
        final data = jsonDecode(response.body) as List<dynamic>;
        return data
            .map((item) =>
                AppNotification.fromJson(item as Map<String, dynamic>))
            .toList();
      default:
        throw Exception('خطا در دریافت اعلان‌ها');
    }
  }

  @override
  Future<int> getUnreadCount() async {
    final url =
        Uri.parse('${ApiConstants.baseUrl}/api/v1/notifications/unread-count');
    final response = await _apiClient.authenticatedGet(url);

    switch (response.statusCode) {
      case 200:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return (data['count'] as num).toInt();
      default:
        throw Exception('خطا در دریافت تعداد اعلان‌های نخوانده');
    }
  }

  @override
  Future<void> markAsRead(String notificationId) async {
    final url = Uri.parse(
        '${ApiConstants.baseUrl}/api/v1/notifications/$notificationId/read');
    final response = await http.put(url, headers: await _authHeaders());

    if (response.statusCode != 200) {
      throw Exception('خطا در علامت‌گذاری اعلان');
    }
  }

  @override
  Future<void> markAllAsRead() async {
    final url = Uri.parse(
        '${ApiConstants.baseUrl}/api/v1/notifications/read-all');
    final response = await http.put(url, headers: await _authHeaders());

    if (response.statusCode != 200) {
      throw Exception('خطا در علامت‌گذاری اعلان‌ها');
    }
  }
}