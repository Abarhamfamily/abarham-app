class Trip {
  final String id;
  final String title;
  final String destination;
  final String? description;
  final DateTime startDate;
  final DateTime endDate;
  final String price;
  final String depositAmount;
  final String? otherVehiclePrice;
  final int capacity;
  final int remainingCapacity;
  final String status;
  final String? transportationType;
  final String? difficultyLevel;
  final String? meetingPoint;
  final String? departureTime;

  const Trip({
    required this.id,
    required this.title,
    required this.destination,
    this.description,
    required this.startDate,
    required this.endDate,
    required this.price,
    required this.depositAmount,
    this.otherVehiclePrice,
    required this.capacity,
    required this.remainingCapacity,
    required this.status,
    this.transportationType,
    this.difficultyLevel,
    this.meetingPoint,
    this.departureTime,
  });

  factory Trip.fromJson(Map<String, dynamic> json) {
    return Trip(
      id: json['id'] as String,
      title: json['title'] as String,
      destination: json['destination'] as String,
      description: json['description'] as String?,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      price: json['price'].toString(),
      depositAmount: json['deposit_amount'].toString(),
      otherVehiclePrice: json['other_vehicle_price']?.toString(),
      capacity: (json['capacity'] as num).toInt(),
      remainingCapacity: (json['remaining_capacity'] as num).toInt(),
      status: json['status'] as String,
      transportationType: json['transportation_type'] as String?,
      difficultyLevel: json['difficulty_level'] as String?,
      meetingPoint: json['meeting_point'] as String?,
      departureTime: json['departure_time'] as String?,
    );
  }
}
