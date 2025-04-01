class MemberModel {
  final String id;
  final String sex;
  final String name;
  final String yyyy;
  final String mm;
  final String dd;
  final String numRecords;

  const MemberModel({
    this.id = '--',
    this.sex = '--',
    this.name = '--',
    this.yyyy = '--',
    this.mm = '--',
    this.dd = '--',
    this.numRecords = '--',
  });
  // 從 JSON 創建 MemberModel
  factory MemberModel.fromJson(Map<String, dynamic> json) {
    return MemberModel(
      id: json['id'] as String? ?? '--',
      sex: json['sex'] as String? ?? '--',
      name: json['name'] as String? ?? '--',
      yyyy: (json['yyyy'] as int?)?.toString() ?? '--', // 將 int 轉為 String
      mm: (json['mm'] as int?)?.toString() ?? '--',
      dd: (json['dd'] as int?)?.toString() ?? '--',
      numRecords: '--', // API 未提供，保持預設值
      //profileImagePath: json['profile_image_path'] as String? ?? '',
      //managerID: json['managerID'] as String? ?? '',
    );
  }
}
