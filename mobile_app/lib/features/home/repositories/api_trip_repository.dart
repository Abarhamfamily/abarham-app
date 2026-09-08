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

    return data.map((item) {
      final trip = item as Map<String, dynamic>;

      return Trip(
        id: trip['id'] as String,
        title: trip['title'] as String,
        destination: trip['destination'] as String,
        description: trip['description'] as String?,
        startDate: DateTime.parse(trip['start_date'] as String),
        endDate: DateTime.parse(trip['end_date'] as String),
        price: trip['price'].toString(),
        depositAmount: trip['deposit_amount'].toString(),
        capacity: (trip['capacity'] as num).toInt(),
        remainingCapacity: (trip['remaining_capacity'] as num).toInt(),
        status: trip['status'] as String,
        transportationType: trip['transportation_type'] as String?,
        difficultyLevel: trip['difficulty_level'] as String?,
        meetingPoint: trip['meeting_point'] as String?,
        departureTime: trip['departure_time'] as String?,
      );
    }).toList();
  }
}
