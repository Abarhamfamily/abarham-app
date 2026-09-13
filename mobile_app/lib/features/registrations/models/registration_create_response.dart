import 'registration.dart';
import 'payment.dart';
import 'waitlist_entry.dart';

class RegistrationCreateResponse {
  final Registration? registration;
  final Payment? payment;
  final WaitlistEntry? waitlistEntry;
  final String message;

  const RegistrationCreateResponse({
    this.registration,
    this.payment,
    this.waitlistEntry,
    required this.message,
  });

  factory RegistrationCreateResponse.fromJson(Map<String, dynamic> json) {
    return RegistrationCreateResponse(
      registration: json['registration'] != null
          ? Registration.fromJson(json['registration'] as Map<String, dynamic>)
          : null,
      payment: json['payment'] != null
          ? Payment.fromJson(json['payment'] as Map<String, dynamic>)
          : null,
      waitlistEntry: json['waitlist_entry'] != null
          ? WaitlistEntry.fromJson(json['waitlist_entry'] as Map<String, dynamic>)
          : null,
      message: json['message'] as String,
    );
  }
}