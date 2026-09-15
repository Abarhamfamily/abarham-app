class AppUser {
  final String id;
  final String phoneNumber;
  final String? email;
  final String fullName;
  final String? nationalId;
  final bool isActive;

  const AppUser({
    required this.id,
    required this.phoneNumber,
    this.email,
    required this.fullName,
    this.nationalId,
    required this.isActive,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] as String,
      phoneNumber: json['phone_number'] as String,
      email: json['email'] as String?,
      fullName: json['full_name'] as String,
      nationalId: json['national_id'] as String?,
      isActive: json['is_active'] as bool,
    );
  }
}

class UserProfileData {
  final String? birthDate;
  final String? emergencyContactName;
  final String? emergencyContactPhone;
  final String? medicalNotes;
  final bool vehicleHasCapacity;
  final int emptySeats;
  final String? profileImageUrl;

  const UserProfileData({
    this.birthDate,
    this.emergencyContactName,
    this.emergencyContactPhone,
    this.medicalNotes,
    required this.vehicleHasCapacity,
    required this.emptySeats,
    this.profileImageUrl,
  });

  factory UserProfileData.fromJson(Map<String, dynamic> json) {
    return UserProfileData(
      birthDate: json['birth_date'] as String?,
      emergencyContactName: json['emergency_contact_name'] as String?,
      emergencyContactPhone: json['emergency_contact_phone'] as String?,
      medicalNotes: json['medical_notes'] as String?,
      vehicleHasCapacity: json['vehicle_has_capacity'] as bool? ?? false,
      emptySeats: (json['empty_seats'] as num?)?.toInt() ?? 0,
      profileImageUrl: json['profile_image_url'] as String?,
    );
  }
}

class UserWithProfile {
  final AppUser user;
  final UserProfileData? profile;

  const UserWithProfile({required this.user, this.profile});

  factory UserWithProfile.fromJson(Map<String, dynamic> json) {
    return UserWithProfile(
      user: AppUser.fromJson(json['user'] as Map<String, dynamic>),
      profile: json['profile'] != null
          ? UserProfileData.fromJson(json['profile'] as Map<String, dynamic>)
          : null,
    );
  }
}