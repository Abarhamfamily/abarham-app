import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/constants/api_constants.dart';
import '../models/trip.dart';
import 'trip_repository.dart';

class ApiTripRepository implements TripRepository {
  @override
  Future<List<Trip>> getTrips() async {
    final response = await http.get(
      Uri.parse('${ApiConstants.baseUrl}/api/v1/trips'),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Failed to load trips: ${response.statusCode}');
    }

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    final data = body['data'] as List<dynamic>;

    return data.map((item) => Trip.fromJson(item as Map<String, dynamic>)).toList();
  }
}
