part of '../pages/home_page.dart';

String _formatTripPrice(String rawPrice) {
  final groups = <String>[];
  var end = rawPrice.length;

  while (end > 0) {
    final start = end > 3 ? end - 3 : 0;
    groups.insert(0, rawPrice.substring(start, end));
    end = start;
  }

  const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
  final localizedPrice = groups.join(',').split('').map((character) {
    final digit = int.tryParse(character);
    return digit == null ? character : persianDigits[digit];
  }).join();

  return '$localizedPrice تومان';
}

class _TripCard extends StatelessWidget {
  final Trip trip;
  final String image;

  const _TripCard({
    required this.trip,
    required this.image,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.of(context).push(
          AppRouter.route(
            builder: (_) => TripDetailsPage(trip: trip),
          ),
        );
      },
      child: Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [
          BoxShadow(
            blurRadius: 8,
            offset: Offset(0, 2),
            color: Color(0x10000000),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Row(
        children: [
          SizedBox(
            width: 120,
            height: 140,
            child: Image.network(
              image,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => Container(
                color: const Color(0xFFDCE7D9),
              ),
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(13),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 7,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: .1),
                      borderRadius: BorderRadius.circular(7),
                    ),
                    child: Text(
                      trip.difficultyLevel ?? '',
                      style: const TextStyle(
                        color: AppColors.primary,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    trip.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: AppColors.foreground,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    trip.destination,
                    style: const TextStyle(
                      fontSize: 11,
                      color: Color(0xFF718078),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _formatTripPrice(trip.price),
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: AppColors.amber,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      ),
    );
  }
}
