class User {
  final String id;
  final String phoneNumber;
  final String fullName;
  final String? email;
  final String? nationalId;
  final bool isActive;

  User({
    required this.id,
    required this.phoneNumber,
    required this.fullName,
    this.email,
    this.nationalId,
    required this.isActive,
  });
}