part of '../pages/home_page.dart';

class _CommunityCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            AppColors.primary,
            Color(0xFF79A65E),
          ],
        ),
        borderRadius: BorderRadius.circular(24),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'آبرهام فراتر از یک آژانس، یک جامعه است',
            style: TextStyle(
              color: Colors.white,
              fontSize: 19,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 10),
          Text(
            'ما فقط سفر نمی‌رویم؛ ما در کنار هم زندگی در طبیعت را تجربه می‌کنیم. به جامعه طبیعت‌گردان آبرهام بپیوندید.',
            style: TextStyle(
              color: Colors.white70,
              height: 1.7,
              fontSize: 12,
            ),
          ),
          SizedBox(height: 16),
          _SmallButton(text: 'کشف سفرها'),
        ],
      ),
    );
  }
}
