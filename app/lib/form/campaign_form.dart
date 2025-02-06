import 'dart:developer';

import 'package:flutter/material.dart';


class CampaignForm extends StatefulWidget {
  // final Campaign? campaign;
  final bool shouldPop;

  // const CampaignForm({ super.key, this.campaign, this.shouldPop = false });
  const CampaignForm({ super.key, this.shouldPop = false });

  @override
  State<CampaignForm> createState() => _CampaignFormState();
}

class _CampaignFormState extends State<CampaignForm> {
  final _formKey = GlobalKey<FormState>();

  final nameController = TextEditingController();

  bool isActive = false;

  @override
  void initState() {
    super.initState();

    // if (widget.campaign != null) {
    //   nameController.text = campaign.name;
    //   isActive = campaign.active;
    // }
  }

  @override
  Widget build(BuildContext context) {
    final nameField = TextFormField(
      keyboardType: TextInputType.number,
      decoration: const InputDecoration(
        border: OutlineInputBorder(),
        label: Text("Nome da Campanha"),
        floatingLabelBehavior: FloatingLabelBehavior.always,
        hintText: "Digite o nome do da campanha"
      ),
      controller: nameController,
      validator: (name) {
        if (name == null) {
          return "Escolha o nome da campanha";
        }

        if (name.length <= 5) {
          return "O nome da campanha deve ter ao menos cinco caracteres.";
        }

        return null;
      }
    );

    final activeSwitch = Switch(
      value: isActive,
      onChanged: (value) => setState(() => isActive = value)
    );

    final saveButton = TextButton(onPressed: saveCampaign, child: const Text("SALVAR"));

    const divider = Divider(height: 8, color: Colors.transparent);

    final column = <Widget>[
      nameField,
      divider,
      saveButton,
      Row(children: [ activeSwitch, const Text("Ativa") ])
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(8.0),
      child: Form(
        autovalidateMode: AutovalidateMode.always,
        key: _formKey,
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: column)
      )
    );
  }

  void saveCampaign() {

  }

  String? validateAllFields() {
    return null;
  }

  void clearForm() {
    setState(() {
      nameController.clear();
      isActive = false;
    });
  }
}
