from pydantic import BaseModel

class BasePromptTemplate(BaseModel):
        promptTemplate: str
        parameterKys: list[str]


class StoryverseMetaData(BaseModel):
    storyVerse: str
    characterGenearationPromptTemplate: BasePromptTemplate
    plotGenerationPromptTemplate: BasePromptTemplate
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