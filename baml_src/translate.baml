function GetLiteralTranslate(context: string, prompt: string, source_lang: string, target_lang: string, is_song: bool) -> string {

  // Specify a client afrom clients.baml
  client Gemini // Set Model
  prompt #"
    {{context}}

    Provide a literal, word-for-word translation of the following text into {{target_lang}}

    <source_text>
    {{ prompt }}
    </source_text>

    After each line or paragraph, provide alternative translations for key terms, ambiguous passages, and any challenging passages.
    Use square brackets to indicate alternatives.
    Include brief explanations and backtranslations of any alternative translations so that even a non-native speaker could understand what the choice means.

    Use bullet points to organize your analysis.

    Return as a markdown string
  "#
}

function GetClarity(context: string, prompt: string, analysis: string, target_lang: string, literal_translation: string) -> string {

  // Specify a client afrom clients.baml
  client Gemini // Set Model
  prompt #"
    {{context}}

    Adapt this literal translation into clear, simple {{target_lang}}, emphasizing clarity while retaining a reasonable amount of the original meaning.

    Likewise, if a line is blank, include a blank line in the output.

    If applicable, write an alternative translation after a phrase or line in square brackets.
    For example, "Amazing grace, how sweet the sound [Stunning grace, how it moves my ear]".
    Don't include backtranslations at this point.

    If there are no reasonable alternatives, simply leave the line as is.

    <original>
    {{prompt}}
    </original>

    <analysis>
    {{analysis}}
    </analysis>

    <literal_translation>
    {{literal_translation}}
    </literal_translation>

    Use bullet points to organize your analysis.

    Return as a markdown string
  "#
}

function GetAnalysis(context: string, target_lang: string, source_text: string, source_lang: string) -> string {
  // Specify a client a from clients.baml
  client Gemini // Set Model
  prompt #"

    {{context}}

    Please provide a detailed analysis of the source text to help guide the translation process.

    <source_text>
    {{source_text}}
    <source_text>

    Outline of the text, with the main ideas of each section
    Provide a detailed analysis of the following aspects:

        1. Theological concepts and terminology, including any specific references to scripture or doctrine. For each concept or reference, describe it in {{source_lang}} and {{target_lang}}, including a complete quote in {{target_lang}} if applicable.
        2. Cultural references
        3. Key metaphors and imagery
        4. Potential translation challenges

    Use bullet points to organize your analysis.

    Return as a markdown string
  "#
}

function GetReview(
  context: string,
  target_lang: string,
  source_text: string,
  clarified_translation: string,
  backtranslation: string,
  syllabification: string | null) -> string {

  client Gemini
  prompt #"
    {{context}}

    Please provide a comprehensive review of the translation, considering:

      1. Accuracy of meaning
      2. Preservation of theological concepts
      3. Cultural appropriateness
      4. Areas for potential improvement

    One or more errors may have been introduced in the translation. Identify and correct them.

    Compare:

    Original:
    {{source_text}}

    Final Translation:
    {{clarified_translation}}

    Backtranslation:
    {{backtranslation}}

    The analysis should include both strengths and weaknesses. Provide specific recommendations for improvement.

    Use bullet points to organize your analysis.

    Return as a markdown string
  "#
}

function GetBackTranslation(
  context: string,
  source_lang: string,
  clarified_translation: string) -> string {

  client Gemini
  prompt #"
    {{context}}

    To verify the translation, we will backtranslate it into the original language.
    Translate the following literally into {{source_lang}}, adding notes as needed in [ ] brackets:

    <translation>
    {{clarified_translation}}
    </translation>
  "#
}

function GetFinalTranslation(
  context: string,
  target_lang: string,
  source_text: string,
  analysis: string,
  clarified_translation: string,
  final_review: string,
  item_type: string
) -> string {
  client Gemini
  prompt #"
    {{context}}

    Based on the analysis, translation, backtranslation, and review, provide a final translation of the {{item_type}} into {{target_lang}}.

    <original>
    {{source_text}}
    </original>

    <analysis>
    {{analysis}}
    </analysis>

    <translation>
    {{clarified_translation}}
    </translation>

    <review>
    {{final_review}}
    </review>

    Use bullet points to organize your analysis.

    Return the tranlation as a simple string.
  "#
}

test analysis{
    functions [GetAnalysis]
    args {
        context "For context, we are translating a text from English to French, aiming for accuracy, simplicity, and clarity. This step is one part of a multi-step process to translate the text. Do only what is asked in each step."
        source_text "For God so loved the world!"
        source_lang "English"
        target_lang "French"
    }
}