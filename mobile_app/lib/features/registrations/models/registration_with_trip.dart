class RegistrationWithTrip {
  final String id;
  final String tripId;
  final String tripTitle;
  final String tripDestination;
  final String status;
  final String totalPrice;
  final String depositPaid;
  final String remainingAmount;
  final int passengerCount;
  final String? vehicleType;
  final String registeredAt;

  const RegistrationWithTrip({
    required this.id,
    required this.tripId,
    required this.tripTitle,
    required this.tripDestination,
    required this.status,
    required this.totalPrice,
    required this.depositPaid,
    required this.remainingAmount,
    required this.passengerCount,
    this.vehicleType,
    required this.registeredAt,
  });

  factory RegistrationWithTrip.fromJson(Map<String, dynamic> json) {
    return RegistrationWithTrip(
      id: json['id'] as String,
      tripId: json['trip_id'] as String,
      tripTitle: json['trip_title'] as String,
      tripDestination: json['trip_destination'] as String,
      status: json['status'] as String,
      totalPrice: json['total_price'].toString(),
      depositPaid: json['deposit_paid'].toString(),
      remainingAmount: json['remaining_amount'].toString(),
      passengerCount: (json['passenger_count'] as num).toInt(),
      vehicleType: json['vehicle_type'] as String?,
      registeredAt: json['registered_at'] as String,
    );
  }
}