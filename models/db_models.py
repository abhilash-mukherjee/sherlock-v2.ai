from pydantic import BaseModel

class ParameterValueDistribution(BaseModel):
    value: str
    probability: float
class PromptParameterDetails(BaseModel):
     key : str
     valueDistribution: list[ParameterValueDistribution]
     chooseMultiple: bool = False
     
class BasePromptTemplateV2(BaseModel):
        promptTemplate: str
        parameterKys: list[str]
        promptParameterDetailsList: list[PromptParameterDetails]

class BasePromptTemplate(BaseModel):
        promptTemplate: str
        parameterKys: list[str]

class CrimeThemeDetails(BaseModel):
     themes : list[str]
     probability: float

class StoryverseMetaData(BaseModel):
    storyVerse: str
    characterGenearationPromptTemplate: BasePromptTemplateV2
    plotGenerationPromptTemplate: BasePromptTemplateV2
    storyChainGenerationPromptTemplate: BasePromptTemplate
    storySummaryGenerationPromptTemplate: BasePromptTemplate
    fistDraftGenerationPromptTemplate: BasePromptTemplate
    climaxEnhancementPromptTemplate: BasePromptTemplate
    storyverseAlignmentPromptTemplate: BasePromptTemplate


class Job(BaseModel):
    storyVerse : str
    characterData: str
    plot: str
    storyChain: str
    storySummary: str
    firstDraft: str
    climaxEnhancedStory: str
    finalStory: str