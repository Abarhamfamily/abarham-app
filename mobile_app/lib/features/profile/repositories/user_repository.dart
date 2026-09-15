import '../models/user_profile.dart';

abstract class UserRepository {
  Future<UserWithProfile> getMyProfile();

  Future<UserProfileData> updateProfile({
    String? birthDate,
    String? emergencyContactName,
    String? emergencyContactPhone,
    String? medicalNotes,
    bool? vehicleHasCapacity,
    int? emptySeats,
  });

  Future<UserProfileData> uploadProfileImage(String filePath);
}