
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/theme/app_colors.dart';
import '../models/user_profile.dart';
import '../repositories/api_user_repository.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final ApiUserRepository _repository = ApiUserRepository();

  late Future<UserWithProfile> _profileFuture;
  bool _isUploadingImage = false;
  bool _isSaving = false;

  final _emergencyNameController = TextEditingController();
  final _emergencyPhoneController = TextEditingController();
  final _medicalNotesController = TextEditingController();
  bool _vehicleHasCapacity = false;
  int _emptySeats = 0;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  void _loadProfile() {
    _profileFuture = _repository.getMyProfile();
    _profileFuture.then((data) {
      if (!mounted) return;
      final profile = data.profile;
      setState(() {
        _emergencyNameController.text = profile?.emergencyContactName ?? '';
        _emergencyPhoneController.text = profile?.emergencyContactPhone ?? '';
        _medicalNotesController.text = profile?.medicalNotes ?? '';
        _vehicleHasCapacity = profile?.vehicleHasCapacity ?? false;
        _emptySeats = profile?.emptySeats ?? 0;
      });
    }).catchError((_) {});
  }

  @override
  void dispose() {
    _emergencyNameController.dispose();
    _emergencyPhoneController.dispose();
    _medicalNotesController.dispose();
    super.dispose();
  }

  Future<void> _handlePickImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1024,
      imageQuality: 85,
    );
    if (picked == null) return;
    if (!mounted) return;

    setState(() => _isUploadingImage = true);

    try {
      await _repository.uploadProfileImage(picked.path);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('عکس پروفایل با موفقیت به‌روزرسانی شد')),
      );
      setState(() {
        _loadProfile();
      });
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() => _isUploadingImage = false);
      }
    }
  }

  Future<void> _handleSave() async {
    setState(() => _isSaving = true);

    try {
      await _repository.updateProfile(
        emergencyContactName: _emergencyNameController.text.trim().isEmpty
            ? null
            : _emergencyNameController.text.trim(),
        emergencyContactPhone: _emergencyPhoneController.text.trim().isEmpty
            ? null
            : _emergencyPhoneController.text.trim(),
        medicalNotes: _medicalNotesController.text.trim().isEmpty
            ? null
            : _medicalNotesController.text.trim(),
        vehicleHasCapacity: _vehicleHasCapacity,
        emptySeats: _emptySeats,
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('اطلاعات پروفایل ذخیره شد')),
      );
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('پروفایل من'),
        ),
        body: FutureBuilder<UserWithProfile>(
          future: _profileFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('دریافت اطلاعات پروفایل با خطا مواجه شد'),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: () => setState(() => _loadProfile()),
                      child: const Text('تلاش مجدد'),
                    ),
                  ],
                ),
              );
            }

            final data = snapshot.data!;
            final imageUrl = data.profile?.profileImageUrl;

            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Center(
                  child: Stack(
                    children: [
                      CircleAvatar(
                        radius: 48,
                        backgroundColor: const Color(0xFFE5E4DC),
                        backgroundImage: imageUrl != null
                            ? NetworkImage('${ApiConstants.baseUrl}$imageUrl')
                            : null,
                        child: imageUrl == null
                            ? const Icon(Icons.person, size: 48, color: Color(0xFF718078))
                            : null,
                      ),
                      Positioned(
                        bottom: 0,
                        left: 0,
                        child: GestureDetector(
                          onTap: _isUploadingImage ? null : _handlePickImage,
                          child: Container(
                            width: 32,
                            height: 32,
                            decoration: const BoxDecoration(
                              color: AppColors.primary,
                              shape: BoxShape.circle,
                            ),
                            child: _isUploadingImage
                                ? const Padding(
                                    padding: EdgeInsets.all(6),
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.white,
                                    ),
                                  )
                                : const Icon(Icons.camera_alt, size: 16, color: Colors.white),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Center(
                  child: Text(
                    data.user.fullName,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppColors.foreground,
                    ),
                  ),
                ),
                Center(
                  child: Text(
                    data.user.phoneNumber,
                    style: const TextStyle(
                      fontSize: 13,
                      color: Color(0xFF718078),
                    ),
                  ),
                ),
                const SizedBox(height: 28),
                const Text(
                  'اطلاعات تماس اضطراری',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: AppColors.foreground,
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _emergencyNameController,
                  decoration: const InputDecoration(
                    labelText: 'نام تماس اضطراری',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _emergencyPhoneController,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'شماره تماس اضطراری',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _medicalNotesController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'یادداشت پزشکی (اختیاری)',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 28),
                const Text(
                  'ظرفیت خودرو',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: AppColors.foreground,
                  ),
                ),
                const SizedBox(height: 8),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('خودروی من ظرفیت خالی دارد'),
                  value: _vehicleHasCapacity,
                  onChanged: (value) {
                    setState(() => _vehicleHasCapacity = value);
                  },
                ),
                if (_vehicleHasCapacity) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Text('تعداد صندلی خالی:'),
                      const SizedBox(width: 12),
                      IconButton(
                        onPressed: _emptySeats > 0
                            ? () => setState(() => _emptySeats -= 1)
                            : null,
                        icon: const Icon(Icons.remove_circle_outline),
                      ),
                      Text('$_emptySeats', style: const TextStyle(fontSize: 16)),
                      IconButton(
                        onPressed: () => setState(() => _emptySeats += 1),
                        icon: const Icon(Icons.add_circle_outline),
                      ),
                    ],
                  ),
                ],
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isSaving ? null : _handleSave,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isSaving
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : const Text(
                            'ذخیره تغییرات',
                            style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                          ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}