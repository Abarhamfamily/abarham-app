part of '../pages/home_page.dart';

class _Categories extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final categories = [
      ('🌲', 'جنگل'),
      ('🏕️', 'کمپ'),
      ('🥾', 'دره‌نوردی'),
      ('⛰️', 'کوهنوردی'),
    ];

    return SizedBox(
      height: 92,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 10),
        itemBuilder: (_, index) {
          final item = categories[index];

          return Container(
            width: 82,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                color: const Color(0xFFE8E6DE),
              ),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  item.$1,
                  style: const TextStyle(fontSize: 27),
                ),
                const SizedBox(height: 6),
                Text(
                  item.$2,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: AppColors.foreground,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
