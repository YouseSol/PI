class Lead {
  int id;
  int campaign;

  String linkedinPublicIdentifier;
  String? chatId;

  String firstName, lastName;

  List<String> emails;
  List<String> phones;

  bool active;

  Lead({
    required this.id,
    required this.campaign,
    required this.linkedinPublicIdentifier,
    required this.chatId,
    required this.firstName,
    required this.lastName,
    required this.emails,
    required this.phones,
    required this.active,
  });

  Lead.fromMap(Map obj):
    id = obj["id"] as int,
    campaign = obj["campaign"] as int,
    linkedinPublicIdentifier = obj["linkedin_public_identifier"] as String,
    chatId = obj["chat_id"] as String?,
    firstName = obj["first_name"] as String,
    lastName = obj["last_name"] as String,
    emails = (obj["emails"] as List<dynamic>).cast<String>(),
    phones = (obj["phones"] as List<dynamic>).cast<String>(),
    active = obj["active"] as bool;

  Map toJson() {
    return {
      'id': id,
      'campaign': campaign,
      'linkedin_public_identifier': linkedinPublicIdentifier,
      'chat_id': chatId,
      'first_name': firstName,
      'last_name': lastName,
      'emails': emails,
      'phones': phones,
      'active': active
    };
  }
}
