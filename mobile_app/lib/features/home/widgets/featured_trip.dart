part of '../pages/home_page.dart';

class _FeaturedTrip extends StatelessWidget {
  final Trip trip;
  final String image;

  const _FeaturedTrip({
    required this.trip,
    required this.image,
  });

  @override
  Widget build(BuildContext context) {
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    final remainingCapacity = trip.remainingCapacity.toString().split('').map((character) {
      final digit = int.parse(character);
      return persianDigits[digit];
    }).join();

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        boxShadow: const [
          BoxShadow(
            blurRadius: 12,
            offset: Offset(0, 3),
            color: Color(0x12000000),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            height: 190,
            width: double.infinity,
            child: Stack(
              fit: StackFit.expand,
              children: [
                Image.network(
                  image,
                  fit: BoxFit.cover,
                ),
                Positioned(
                  top: 14,
                  right: 14,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(9),
                    ),
                    child: Text(
                      trip.difficultyLevel ?? '',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  trip.title,
                  style: TextStyle(
                    fontSize: 19,
                    fontWeight: FontWeight.bold,
                    color: AppColors.foreground,
                  ),
                ),
                const SizedBox(height: 9),
                Row(
                  children: [
                    Icon(
                      Icons.location_on_outlined,
                      size: 17,
                      color: AppColors.primary,
                    ),
                    SizedBox(width: 4),
                    Text(
                      trip.destination,
                      style: TextStyle(
                        fontSize: 12,
                        color: Color(0xFF718078),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Text(
                      _formatTripPrice(trip.price).replaceFirst(' تومان', ''),
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: AppColors.amber,
                      ),
                    ),
                    const SizedBox(width: 4),
                    const Text(
                      'تومان',
                      style: TextStyle(
                        fontSize: 11,
                        color: Color(0xFF718078),
                      ),
                    ),
                    const Spacer(),
                    const Icon(
                      Icons.people_outline,
                      size: 17,
                      color: AppColors.primary,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '$remainingCapacity نفر ظرفیت باقی‌مانده',
                      style: TextStyle(
                        fontSize: 11,
                        color: Color(0xFF718078),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                GestureDetector(
                  onTap: () {
                    Navigator.of(context).push(
                      AppRouter.route(
                        builder: (_) => TripDetailsPage(trip: trip),
                      ),
                    );
                  },
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 11),
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(14),
                    ),
                    alignment: Alignment.center,
                    child: const Text(
                      'مشاهده بلیت و جزئیات',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
