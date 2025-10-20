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

class AudioChunk(BaseModel):
    chunkId: str
    text: str
    outputAudioFilePath: str


class Job(BaseModel):
    storyVerse : str
    characterData: str
    plot: str
    storyChain: str
    storySummary: str
    firstDraft: str
    climaxEnhancedStory: str
    finalStory: str
    audioChunks: list[AudioChunk] = []
    finalAudioFilePath: str = ""


class TrainingDataGenMetaData(BaseModel):
    storyVerse: str
    storyVerseSystemPrompt: str
    characterGenearationReversePrompt: str
    characterInputPomptGenrationPrompt: str
    plotGenerationReversePrompt: str
    plotCrimeThemeExtractionPrompt: str
    storyChainGenerationReversePrompt: str
    storySummaryGenerationReversePrompt: str
    fistDraftGenerationReversePrompt: str

class TrainingIOPair(BaseModel):
    storyVerse: str
    storyTitle: str
    pipelineStepName: str
    reverseOutputPrompt: str
    inputPromptForFineTuning: str
    modelOutput: str
    systemPrompt: str
    createdAt: int
