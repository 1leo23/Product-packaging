import 'package:flutter/material.dart';
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/widgets/add_member_widget.dart';
import 'package:trajectory_app/widgets/member_list_widget.dart';
import 'package:trajectory_app/widgets/profile_widget.dart';
import 'package:trajectory_app/widgets/side_menu_widget.dart';
import 'package:trajectory_app/widgets/upload_form_widget.dart';

class ManagerScreen extends StatefulWidget {
  const ManagerScreen({super.key});

  @override
  State<ManagerScreen> createState() => _ManagerScreenState();
}

class _ManagerScreenState extends State<ManagerScreen> {
  int _selectedIndex = 0;
  void onMenuTap(int index) {
    setState(() {
      if (index == 3) {
        Navigator.pop(context);
        return;
      }
      _selectedIndex = index;
    });
  }

  final mainWidgetList = <Widget>[
    MemberListWidget(),
    UploadFormWidget(),
    AddMemberWidget(),
  ];
  final profileWidgetList = <Widget>[
    ProfileWidget(type: 'manager'),
    ProfileWidget(type: 'member'),
    ProfileWidget(type: 'member'),
  ];
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _appBar(),

      body: SafeArea(
        child: _buildPage(
          SideMenuWidget(
            type: 'manager',
            selectedIndex: _selectedIndex,
            onMenuTap: onMenuTap,
          ),
          mainWidgetList[_selectedIndex],
          profileWidgetList[_selectedIndex],
        ),
      ),
    );
  }
}

Row _buildPage(
  SideMenuWidget sideMenuWidget,
  Widget mainWidget,
  Widget profileWidget,
) {
  return Row(
    children: [
      // Expanded (彈性布局)，通常用於Row和Col，使用flex分配空間比例，flex總和為12
      Expanded(flex: 2, child: SizedBox(child: sideMenuWidget)),
      Expanded(flex: 9, child: SizedBox(child: mainWidget)),
      Expanded(flex: 3, child: SizedBox(child: profileWidget)),
    ],
  );
}

AppBar _appBar() {
  return AppBar(
    title: Padding(
      padding: const EdgeInsets.only(left: 25),
      child: Text(
        "Trajectory",
        style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
      ),
    ),
    backgroundColor: appBarColor,
  );
}
