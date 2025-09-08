from pydantic import BaseModel

class BasePromptTemplate(BaseModel):
        promptTemplate: str
        parameterKys: list[str]

class CharacterData(BaseModel):
     data: str

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
    characterData: CharacterData
    plot: dict
    storyChain: dict
    storySummary: str
    firstDraft: str
    climaxEnhancedStory: str
    finalStory: str