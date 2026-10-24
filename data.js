/* All teaching content lives here. Keep option strings unique. */
window.POTION_DATA = {
  rounds: [
    { title: 'Find the Irregular Plurals', instruction: 'Find the irregular plural nouns. Add ONLY the correct words to the cauldron!', short: 'The mouse potion', total: 6, animal: 'mouse', plural: 'mice', count: 5, group: 'mice-five', color: 'olive' },
    { title: 'Choose the Correct Form', instruction: 'Choose the correct plural form. Add it to the potion!', short: 'The goose potion', total: 10, animal: 'goose', plural: 'geese', count: 4, group: 'geese-four', color: 'amber' },
    { title: 'Fix the Witch’s Mistakes', instruction: "Check the witch's phrases. Keep the correct ones and fix the mistakes!", short: 'The sheep potion', total: 12, animal: 'sheep', plural: 'sheep', count: 6, group: 'sheep-six', color: 'lilac' }
  ],
  ingredients: [
    { word: 'mice', correct: true }, { word: 'teeth', correct: true },
    { word: 'children', correct: true }, { word: 'geese', correct: true },
    { word: 'men', correct: true }, { word: 'women', correct: true },
    { word: 'pumpkins', correct: false }, { word: 'ghosts', correct: false },
    { word: 'bats', correct: false }, { word: 'witches', correct: false },
    { word: 'spiders', correct: false }, { word: 'cats', correct: false }
  ],
  forms: [
    { word: 'mouse', options: ['mice', 'mouses', 'mouse'], answer: 'mice' },
    { word: 'goose', options: ['gooses', 'geese', 'goose'], answer: 'geese' },
    { word: 'foot', options: ['foots', 'feet', 'feets'], answer: 'feet' },
    { word: 'tooth', options: ['teeth', 'tooths', 'toothes'], answer: 'teeth' },
    { word: 'child', options: ['childs', 'childes', 'children'], answer: 'children' },
    { word: 'person', options: ['people', 'peoples', 'person'], answer: 'people' },
    { word: 'man', options: ['mans', 'men', 'mens'], answer: 'men' },
    { word: 'woman', options: ['womans', 'womens', 'women'], answer: 'women' },
    { word: 'deer', options: ['deers', 'deer', 'deeres'], answer: 'deer' },
    { word: 'ox', options: ['oxes', 'oxen', 'oxs'], answer: 'oxen' }
  ],
  phrases: [
    { phrase: 'three mouses', answer: 'three mice', options: ['three mice', 'three mices', 'three mouse'] },
    { phrase: 'two deers', answer: 'two deer', options: ['two deer', 'two deeres', 'two deers'] },
    { phrase: 'four leafs', answer: 'four leaves', options: ['four leaves', 'four leafes', 'four leafs'] },
    { phrase: 'five knifes', answer: 'five knives', options: ['five knives', 'five knive', 'five knifes'] },
    { phrase: 'six sheeps', answer: 'six sheep', options: ['six sheep', 'six sheepes', 'six sheeps'] },
    { phrase: 'two wolfs', answer: 'two wolves', options: ['two wolves', 'two wolfes', 'two wolfs'] },
    { phrase: 'three men', answer: 'three men', keep: true },
    { phrase: 'four womans', answer: 'four women', options: ['four women', 'four womens', 'four womans'] },
    { phrase: 'two oxes', answer: 'two oxen', options: ['two oxen', 'two oxens', 'two oxes'] },
    { phrase: 'five potatos', answer: 'five potatoes', options: ['five potatoes', 'five potato', 'five potatos'] },
    { phrase: 'seven fish', answer: 'seven fish', keep: true },
    { phrase: 'three children', answer: 'three children', keep: true }
  ]
};
