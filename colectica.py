"""
    Pull information using python ColecticaPortal api
"""

from io import StringIO
import xml.etree.ElementTree as ET
import pandas as pd
import json
import api


def remove_xml_ns(xml):
    """
    Read xml from string, remove namespaces, return root
    """
    it = ET.iterparse(StringIO(xml))
    for _, el in it:
        prefix, has_namespace, postfix = el.tag.partition('}')
        if has_namespace:
            el.tag = postfix  # strip all namespaces
    root = it.root
    return root


def root_to_dict_study(root):
    """
    Part of parse xml, item_type = Study
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    # Sweep Description
    sweep = {}
    sweep['title'] = root.find('.//Citation/Title/String').text
    sweep['principal_investigator'] = root.find('.//Citation/Creator/CreatorName/String').text
    if root.find('.//Citation/Publisher') is not None:
        sweep['publisher'] = root.find('.//Citation/Publisher/PublisherName/String').text
    else:
        sweep['publisher'] = None
    sweep['abstract'] = root.find('.//Abstract/Content').text
    pop = {}
    if root.find('.//UniverseReference') is not None:
        pop['Agency'] = root.find('.//UniverseReference/Agency').text
        pop['ID'] = root.find('.//UniverseReference/ID').text
        pop['Version'] = root.find('.//UniverseReference/Version').text
        pop['Type'] = root.find('.//UniverseReference/TypeOfObject').text
    sweep['population'] = pop
    # custom filed
    CustomFields = root.findall('.//UserAttributePair/AttributeValue')
    custom_list = []
    for x, cus in enumerate(CustomFields):
        # Convert a string representation of a dictionary to a dictionary
        custom_list.append(json.loads(cus.text))
    sweep['custom_field'] = custom_list
    info['sweep'] = sweep

    # Funding
    funding = {}
    organization = {}
    organization['Agency'] = root.find('.//FundingInformation/AgencyOrganizationReference/Agency').text
    organization['ID'] = root.find('.//FundingInformation/AgencyOrganizationReference/ID').text
    organization['Version'] = root.find('.//FundingInformation/AgencyOrganizationReference/Version').text
    organization['Type'] = root.find('.//FundingInformation/AgencyOrganizationReference/TypeOfObject').text
    funding['organization'] = organization
    info['funding'] = funding
    # TODO: Coverage
    coverages = root.findall('.//Coverage')
    # Data
    data = {}
    k = root.find('.//KindOfData')
    data['KindOfData'] = '-'.join(item.text for item in k)
    data['Analysis Unit'] = root.find('.//AnalysisUnit').text
    # data files
    datafile = {}
    if root.find('.//PhysicalInstanceReference') is not None:
        datafile['Agency'] = root.find('.//PhysicalInstanceReference/Agency').text
        datafile['ID'] = root.find('.//PhysicalInstanceReference/ID').text
        datafile['Version'] = root.find('.//PhysicalInstanceReference/Version').text
        datafile['Type'] = root.find('.//PhysicalInstanceReference/TypeOfObject').text
    data['Data File'] = datafile
    info['data'] = data
    # data collection
    datacol = {}
    datacol['Agency'] = root.find('.//DataCollectionReference/Agency').text
    datacol['ID'] = root.find('.//DataCollectionReference/ID').text
    datacol['Version'] = root.find('.//DataCollectionReference/Version').text
    datacol['Type'] = root.find('.//DataCollectionReference/TypeOfObject').text
    info['Data Collection'] = datacol
    # Extra
    metadata = {}
    if root.find('.//RequiredResourcePackages/ResourcePackageReference') is not None:
        metadata['Agency'] = root.find('.//RequiredResourcePackages/ResourcePackageReference/Agency').text
        metadata['ID'] = root.find('.//RequiredResourcePackages/ResourcePackageReference/ID').text
        metadata['Version'] = root.find('.//RequiredResourcePackages/ResourcePackageReference/Version').text
        metadata['Type'] = root.find('.//RequiredResourcePackages/ResourcePackageReference/TypeOfObject').text
    info['Metadata Packages'] = metadata
    return info


def root_to_dict_series(root):
    """
    Part of parse xml, item_type = Series
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    # Study Description
    study = {}
    study['title'] = root.find('.//Citation/Title/String').text
    study['principal_investigator'] = root.find('.//Citation/Creator/CreatorName/String').text
    study['publisher'] = root.find('.//Citation/Publisher/PublisherName/String').text
    study['rights'] = root.find('.//Citation/Copyright/String').text
    study['abstract'] = root.find('.//Abstract/Content').text
    pop = {}
    pop['Agency'] = root.find('.//UniverseReference/Agency').text
    pop['ID'] = root.find('.//UniverseReference/ID').text
    pop['Version'] = root.find('.//UniverseReference/Version').text
    pop['Type'] = root.find('.//UniverseReference/TypeOfObject').text
    study['population'] = pop
    info['study'] = study
    # Funding
    funding = {}
    if not root.find('.//FundingInformation/GrantNumber') is None:
        funding['GrantNumber'] = root.find('.//FundingInformation/GrantNumber').text
    organization = {}
    organization['Agency'] = root.find('.//FundingInformation/AgencyOrganizationReference/Agency').text
    organization['ID'] = root.find('.//FundingInformation/AgencyOrganizationReference/ID').text
    organization['Version'] = root.find('.//FundingInformation/AgencyOrganizationReference/Version').text
    organization['Type'] = root.find('.//FundingInformation/AgencyOrganizationReference/TypeOfObject').text
    funding['organization'] = organization
    info['funding'] = funding
    # Studies
    studies = root.findall('.//StudyUnitReference')
    study_list = []
    for x, study in enumerate(studies):
        study_dict={}
        study_dict['position'] = x + 1
        study_dict['Agency'] = study.find(".//Agency").text
        study_dict['ID'] = study.find(".//ID").text
        study_dict['Version'] = study.find(".//Version").text
        study_dict['Type'] = study.find(".//TypeOfObject").text
        study_list.append(study_dict)
    info['study'] = study_list
    return info


def root_to_dict_data_collection(root):
    """
    Part of parse xml, item_type = Data Collection
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    info['Name'] = root.find('.//DataCollectionModuleName/String').text
    info['Label'] = root.find('.//Label/Content').text
    # InstrumentRef
    cus_dict = {}
    cus = root.findall('.//UserAttributePair')
    for item in cus:
        k = item.find('.//AttributeKey').text.split(':')[-1]
        v = item.find('.//AttributeValue').text.replace('[','').replace(']','').replace('"', '').replace("'","")
        cus_dict[k] = v
    info['Ref'] = cus_dict

    # CollectionEvent
    event = {}
    event['URN'] = root.find('.//CollectionEvent/URN').text
    event['Agency'] = root.find('.//CollectionEvent/Agency').text
    event['ID'] = root.find('.//CollectionEvent/ID').text
    event['Version'] = root.find('.//CollectionEvent/Version').text
    # Organization Reference
    organization_list = []
    organization_all = root.findall('.//CollectionEvent/DataCollectorOrganizationReference')
    for organization in organization_all:
        OrganizationRef = {}
        OrganizationRef['Agency'] = organization.find('.//Agency').text
        OrganizationRef['ID'] = organization.find('.//ID').text
        OrganizationRef['Version'] = organization.find('.//Version').text
        OrganizationRef['Type'] = organization.find('.//TypeOfObject').text
    event['OrganizationRef'] = organization_list

    # Data Collection Date
    DCDate = {}
    date = root.find('.//CollectionEvent/DataCollectionDate')
    if date.find('.//StartDate') is not None:
        DCDate['StartDate'] = date.find('.//StartDate').text
    elif date.find('.//EndDate') is not None:
        DCDate['EndDate'] = date.find('.//EndDate').text
    elif date.find('.//SimpleDate') is not None:
        DCDate['SimpleDate'] = date.find('.//SimpleDate').text
    event['Date'] = DCDate
    # Mode Of Collection
    mode_list = []
    mode_all = root.findall('.//CollectionEvent/ModeOfCollection')
    # list multiple types
    for type_mode in mode_all:
        mode_dict = {}
        mode_dict['URN'] = type_mode.find('./URN').text
        mode_dict['Agency'] = type_mode.find('./Agency').text
        mode_dict['ID'] = type_mode.find('./ID').text
        mode_dict['Version'] = type_mode.find('./Version').text
        mode_dict['TypeOfMode'] = type_mode.find('./TypeOfModeOfCollection').text
        mode_dict['Description'] = type_mode.find('./Description/Content').text
        mode_list.append(mode_dict)
    event['ModeOfCollection'] = mode_list
    info['CollectionEvent'] = event
    # Question Scheme Reference
    QSR = {}
    if root.find('.//QuestionSchemeReference') is not None:
        QSR['Agency'] = root.find('.//QuestionSchemeReference/Agency').text
        QSR['ID'] = root.find('.//QuestionSchemeReference/ID').text
        QSR['Version'] = root.find('.//QuestionSchemeReference/Version').text
        QSR['TypeOfObject'] = root.find('.//QuestionSchemeReference/TypeOfObject').text
    info['reference'] = QSR
    return info


def root_to_dict_sequence(root):
    """
    Part of parse xml, item_type = Sequence
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    info['SourceId'] = root.find('.//UserID').text
    info['ConstructName'] = root.find('.//ConstructName/String').text
    info['Label'] = root.find('.//Label/Content').text
    references = root.findall(".//ControlConstructReference")
    ref_list = []
    for x, ref in enumerate(references):
        ref_dict={}
        ref_dict['position'] = x + 1
        ref_dict['Agency'] = ref.find(".//Agency").text
        ref_dict['ID'] = ref.find(".//ID").text
        ref_dict['Version'] = ref.find(".//Version").text
        ref_dict['Type'] = ref.find(".//TypeOfObject").text
        ref_list.append(ref_dict)
    info['references'] = ref_list
    return info


def root_to_dict_statement(root):
    """
    Part of parse xml, item_type = Statement
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    info['SourceId'] = root.find('.//UserID').text
    instruction = root.find(".//UserAttributePair/AttributeValue").text
    if instruction == '{}':
        info['Instruction'] = ''
    else:
        info['Instruction'] = instruction
    info['Label'] = root.find(".//ConstructName/String").text
    info['Literal'] = root.find(".//DisplayText/LiteralText/Text").text
    return info


def root_to_dict_organization(root):
    """
    Part of parse xml, item_type = Organization
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    # Nickname
    cus_dict = {}
    cus = root.findall('.//UserAttributePair')
    for item in cus:
        k = item.find('.//AttributeKey').text.split(':')[-1]
        v = item.find('.//AttributeValue').text
        cus_dict[k] = v
    info['cust'] = cus_dict
    info['Name'] = root.find('.//OrganizationIdentification/OrganizationName/String').text
    info['Image'] = root.find('.//OrganizationIdentification/OrganizationImage/ImageLocation').text
    info['Description'] = root.find('.//Description/Content').text
    return info


def root_to_dict_instrument(root):
    """
    Part of parse xml, item_type = Instrument
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    if root.findall(".//*[@typeOfUserID='colectica:sourceId']") != []:
        info['InstrumentSourceID'] = root.findall(".//*[@typeOfUserID='colectica:sourceId']")[0].text 
    if root.findall(".//*[@typeOfUserID='closer:sourceFileName']") != []:
        info['InstrumentLabel'] = root.findall(".//*[@typeOfUserID='closer:sourceFileName']")[0].text
    info['InstrumentName'] = root.find(".//InstrumentName/String").text
    info['ExternalInstrumentLocation'] = root.find(".//ExternalInstrumentLocation").text
    references = root.findall(".//ControlConstructReference")
    ref_list = []
    for x, ref in enumerate(references):
        ref_dict={}
        ref_dict['position'] = x + 1
        ref_dict['Agency'] = ref.find(".//Agency").text
        ref_dict['ID'] = ref.find(".//ID").text
        ref_dict['Version'] = ref.find(".//Version").text
        ref_dict['Type'] = ref.find(".//TypeOfObject").text
        ref_list.append(ref_dict)
    info['references'] = ref_list
    return info


def root_to_dict_question_group(root):
    """
    Part of parse xml, item_type = Question Group
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    if root.find('.//QuestionGroupName/String') is not None:
        info['Name'] = root.find('.//QuestionGroupName/String').text
    else:
        info['Name'] = None
    if root.find('.//Label/Content').text is not None:
        info['Label'] = root.find('.//Label/Content').text
    else:
        info['Label'] = None

    # Concept Reference
    ConceptRef = {}
    if root.find('.//ConceptReference') is not None:
        ConceptRef['Agency'] = root.find('.//ConceptReference/Agency').text
        ConceptRef['ID'] = root.find('.//ConceptReference/ID').text
        ConceptRef['Version'] = root.find('.//ConceptReference/Version').text
        ConceptRef['Type'] = root.find('.//ConceptReference/TypeOfObject').text
    info['ConceptRef'] = ConceptRef
    # Question Item Reference
    QuestionItemRef = root.findall(".//QuestionItemReference")
    QIref_list = []
    for x, ref in enumerate(QuestionItemRef):
        ref_dict={}
        ref_dict['position'] = x + 1
        ref_dict['Agency'] = ref.find(".//Agency").text
        ref_dict['ID'] = ref.find(".//ID").text
        ref_dict['Version'] = ref.find(".//Version").text
        ref_dict['Type'] = ref.find(".//TypeOfObject").text
        QIref_list.append(ref_dict)
    info['QuestionItemRef'] = QIref_list
    # Question Group Reference
    QuestionGroupRef = root.findall(".//QuestionGroupReference")
    QGref_list = []
    for x, ref in enumerate(QuestionGroupRef):
        ref_dict={}
        ref_dict['position'] = x + 1
        ref_dict['Agency'] = ref.find(".//Agency").text
        ref_dict['ID'] = ref.find(".//ID").text
        ref_dict['Version'] = ref.find(".//Version").text
        ref_dict['Type'] = ref.find(".//TypeOfObject").text
        QGref_list.append(ref_dict)
    info['QuestionGroupRef'] = QGref_list
    return info


def root_to_dict_concept(root):
    """
    Part of parse xml, item_type = Concept
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    info['VersionResponsibility'] = root.find('.//VersionResponsibility').text
    info['VersionRationale'] = root.find('.//VersionRationale/RationaleDescription/String').text
    info['Name'] = root.find('.//ConceptName/String').text
    info['Label'] = root.find('.//Label/Content').text
    return info


def root_to_dict_interviewer_instruction(root):
    """
    Part of parse xml, item_type = Interviewer Instruction
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    info['UserID'] = root.find('.//UserID').text
    info['InstructionText'] = root.find('.//InstructionText/LiteralText/Text').text
    return info   


def root_to_dict_question(root):
    """
    Part of parse xml, item_type = Question
    """
    info = {}
    info['QuestionURN'] = root.find('.//URN').text
    info['QuestionUserID'] = root.find('.//UserID').text
    QLabel = root.find('.//UserAttributePair/AttributeValue').text
    info['QuestionLabel'] = list(eval(QLabel).values())[0]
    info['QuestionItemName'] = root.find(".//QuestionItemName/String").text
    if root.find(".//QuestionText/LiteralText/Text") is not None:
        info['QuestionLiteral'] = root.find(".//QuestionText/LiteralText/Text").text
    else:
        info['QuestionLiteral'] = None
    # ResponseCardinality
    cardinality = root.find('.//ResponseCardinality')
    car_dict = {}
    car_dict['minimumResponses'] = cardinality.attrib['minimumResponses']
    car_dict['maximumResponses'] = cardinality.attrib['maximumResponses']
    info['ResponseCardinality'] = car_dict
    # response
    response = {}
    CodeDomain = root.find(".//CodeDomain")
    TextDomain = root.find(".//TextDomain")
    NumericDomain = root.find(".//NumericDomain")
    DateTimeDomain = root.find(".//DateTimeDomain")
    if CodeDomain is not None:
        response['response_type'] = 'CodeList'
        response['CodeList_Agency'] = root.find('.//CodeListReference/Agency').text         
        response['CodeList_ID'] = CodeDomain.find(".//CodeListReference/ID").text
        response['CodeList_version'] = CodeDomain.find(".//CodeListReference/Version").text
        response['code_list_URN'] = (':').join(['urn:ddi', response['CodeList_Agency'], response['CodeList_ID'], response['CodeList_version']])      
    elif TextDomain is not None:
        response['response_type'] = 'Text'
        response['response_label'] = TextDomain.find(".//Label/Content").text
    elif NumericDomain is not None:
        response['response_type'] = 'Numeric'
        response['response_label'] = root.find(".//Label").text
        response['response_NumericType'] = root.find(".//NumericTypeCode").text
        if root.find(".//NumberRange/Low") is not None:
            response['response_RangeLow'] = root.find(".//NumberRange/Low").text        
        else:
            response['response_RangeLow'] = None
        if root.find(".//NumberRange/High") is not None:
            response['response_RangeHigh'] = root.find(".//NumberRange/High").text
        else:
            response['response_RangeHigh'] = None
    elif DateTimeDomain is not None:
        response['response_type'] = 'DateTime'
        response['DateTypeCode'] = DateTimeDomain.find(".//DateTypeCode").text
        response['Label'] = DateTimeDomain.find(".//Label/Content").text

    info['Response'] = response

    # InterviewerInstructionReference
    inst_dict = {}
    InstructionRef = root.find(".//InterviewerInstructionReference")
    if InstructionRef is not None:
        inst_dict['Agency'] = InstructionRef.find(".//Agency").text
        inst_dict['ID'] = InstructionRef.find(".//ID").text
        inst_dict['Version'] = InstructionRef.find(".//Version").text
        inst_dict['Type'] = InstructionRef.find(".//TypeOfObject").text
    info['Instruction'] = inst_dict
    return info


def root_to_dict_code_set(root):
    """
    Part of parse xml, item_type = Code Set
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    return info


def root_to_dict_code(root):
    """
    Part of parse xml, item_type = Code
    """
    info = {}
    info['URN'] = root.find('.//URN').text
    info['SourceId'] = root.find('.//UserID').text
    info['Label'] = root.find('.//Label/Content').text
    # Code
    Code = root.findall('//Code')
    return info


def parse_xml(xml, item_type):
    """
    Used for parsing Item value
    item_type in:
        - Series
        - Study
        - Data Collection
        - Sequence
        - Statement
        - Organization
        - Instrument
        - Question Group
        - Concept
        - Question
        - Code Set
        - Interviewer Instruction
    """
    root = remove_xml_ns(xml)

    if item_type == 'Series':
        info = root_to_dict_series(root)
    elif item_type == 'Study':
        info = root_to_dict_study(root)
    elif item_type == 'Data Collection':
        info = root_to_dict_data_collection(root)
    elif item_type == 'Sequence':
        info = root_to_dict_sequence(root)
    elif item_type == 'Statement':
        info = root_to_dict_statement(root)
    elif item_type == 'Organization':
        info = root_to_dict_organization(root)
    elif item_type == 'Instrument':
        info = root_to_dict_instrument(root)
    elif item_type == 'Question Group':
        info = root_to_dict_question_group(root)
    elif item_type == 'Concept':
        info = root_to_dict_concept(root)
    elif item_type == 'Question':
        info = root_to_dict_question(root)
    elif item_type == 'Code Set':
        info = root_to_dict_code_set(root)
    elif item_type == 'Interviewer Instruction':
        info = root_to_dict_interviewer_instruction(root)
    else:
        info = {}
    return info


class ColecticaObject(api.ColecticaLowLevelAPI):
    """Ask practical questions to Colectica."""

    def item_to_dict(self, AgencyId, Identifier):
        """
        From an agency ID and an identifier, get information using get_an_item
        Return a dictionary
        """
        result = self.get_an_item(AgencyId, Identifier)

        info = {}
        for k, v in result.items():
            if k == 'ItemType':
                info[k] = self.item_code_inv(v)
            elif k == 'Item':
                item_info = parse_xml(v, self.item_code_inv(result['ItemType']))
            else:
                info[k] = v

        return {**info, **item_info}


    def get_a_set_to_df(self, AgencyId, Identifier, Version):
        """
        From a study, find all questions
        Example:
            'ItemType': 'f196cc07-9c99-4725-ad55-5b34f479cf7d', (Instrument)
            'AgencyId': 'uk.cls.nextsteps',
            'Version': 1,
            'Identifier': 'a6f96245-5c00-4ad3-89e9-79afaefa0c28'
        """

        l = self.get_a_set_typed(AgencyId, Identifier, Version)
        # print(l)
        df = pd.DataFrame(
             [self.item_code_inv(l[i]["Item2"]), l[i]["Item1"]["Item1"]] for i in range(len(l))
         )
        df.columns = ["ItemType", "Identifier"]

        return df


    def item_info_set(self, AgencyId, Identifier):
        """
        From an ID, find it's name and set
        """
        info = self.item_to_dict(AgencyId, Identifier)
        df = self.get_a_set_to_df(AgencyId, Identifier, str(info['Version']))
        return df, info


    def get_question_group_info(self, AgencyId, Identifier):
        """
        From a question identifier, get information about it
        """
        question_group = self.get_an_item(AgencyId, Identifier)
        root = remove_xml_ns(question_group["Item"])

        question = {}
        for k, v in question_result.items():
            if k == 'ItemType':
                question[k] = self.item_code_inv(v)
            elif k == 'Item':
                question['UserID'] = root.find(".//UserID").text
                question['QuestionLabel'] = root.find(".//UserAttributePair/AttributeValue").text
                question['QuestionItemName'] = root.find(".//QuestionItemName/String").text
                question['QuestionLiteral'] = root.find(".//QuestionText/LiteralText/Text").text
            else:
                question[k] = v
        return question


    def get_question_all(self, AgencyId, Identifier):
        """
        From a question ID, return question info and it's response
        """
        # print(AgencyId, Identifier)
        question_info = self.item_to_dict(AgencyId, Identifier)
        question_data = [ [ question_info['QuestionURN'],
                            question_info['QuestionUserID'],
                            question_info['QuestionLabel'],
                            question_info['QuestionItemName'],
                            question_info['QuestionLiteral'],
                            question_info['Response']['response_type'] ] ]

        df_question = pd.DataFrame(question_data,
                                   columns=['QuestionURN', 'QuestionUserID', 'QuestionLabel', 'QuestionItemName', 
                                            'QuestionLiteral', 'response_type'])

        # instruction
        if question_info['Instruction'] != {}:
            instruction_dict = self.item_to_dict(question_info['Instruction']['Agency'], question_info['Instruction']['ID'])
            df_question['Instruction_URN'] = instruction_dict['URN']
            df_question['Instruction'] = instruction_dict['InstructionText']
        else:
            df_question['Instruction_URN'] = None
            df_question['Instruction'] = None

        if question_info['Response']['response_type'] == 'CodeList':
            code_result = self.get_an_item(AgencyId, question_info['Response']['CodeList_ID'])
            root = remove_xml_ns(code_result["Item"])

            code_list_sourceId = root.find(".//UserID").text
            code_list_label = root.find(".//Label/Content").text

            category = [i.text for i in root.findall(".//Code/CategoryReference/ID")]

            df = pd.DataFrame(columns=["response_type", "Name", "ID", "Label"])

            for c in category:
                item_result = self.get_an_item(AgencyId, c)
                root = remove_xml_ns(item_result["Item"])

                CategoryName = root.find(".//CategoryName/String").text
                UserID = root.find(".//UserID").text
                Label = root.find(".//Label/Content").text
                df = df.append({"response_type": "CodeList",
                                         "Name": CategoryName,
                                           "ID": UserID,
                                        "Label": Label
                               }, ignore_index=True)

            df['code_list_URN'] = question_info['Response']['code_list_URN']
            df['code_list_sourceId'] = code_list_sourceId
            df['code_list_label'] = code_list_label
            df['Order'] = df.index + 1
            df['QuestionURN'] = question_info['QuestionURN']
            df['QuestionItemName'] = question_info['QuestionItemName']

            df_question['response'] = code_list_label
            df_question['response_domain'] = question_info['Response']['code_list_URN']

        elif question_info['Response']['response_type'] == 'Text':
            data = [ [ question_info['QuestionURN'],
                       question_info['QuestionItemName'],
                       question_info['Response']['response_type'],
                       question_info['Response']['response_label'] ] ]
            df = pd.DataFrame(data, columns=['QuestionURN', 'QuestionItemName', 'response_type', 'Label'])

            df_question['response'] = question_info['Response']['response_label']

        elif question_info['Response']['response_type'] == 'Numeric':
            data = [ [ question_info['QuestionURN'],
                       question_info['QuestionItemName'], 
                       question_info['Response']['response_type'], 
                       question_info['Response']['response_label'],
                       question_info['Response']['response_NumericType'],
                       question_info['Response']['response_RangeLow'],
                       question_info['Response']['response_RangeHigh'] ] ]
            df = pd.DataFrame(data, columns=['QuestionURN', 'QuestionItemName', 'response_type', 'Label', 'response_NumericType', 'response_RangeLow', 'response_RangeHigh'])

            df_question['response'] = question_info['Response']['response_label']

        else:
            print(question_info['Response']['response_type'])
            df = pd.DataFrame()

        return df_question, df


if __name__ == "__main__":
    raise RuntimeError("don't run this directly")

