part of '../pages/home_page.dart';

class _BottomNavigation extends StatelessWidget {
  const _BottomNavigation();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: .94),
        border: const Border(
          top: BorderSide(
            color: Color(0xFFE5E4DC),
          ),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.only(
            top: 7,
            bottom: 7,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: const [
              _NavItem(
                icon: Icons.home_rounded,
                label: 'خانه',
                active: true,
              ),
              _NavItem(
                icon: Icons.hiking_rounded,
                label: 'سفرها',
              ),
              _NavItem(
                icon: Icons.account_balance_wallet_rounded,
                label: 'کیف سفر',
              ),
              _NavItem(
                icon: Icons.person_rounded,
                label: 'پروفایل',
              ),
            ],
          ),
        ),
      ),
    );
  }
}
