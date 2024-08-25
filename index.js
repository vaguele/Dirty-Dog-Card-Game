const cardObjectDefinition = [
    {id: 1, imagePath: 'images/king_of_hearts2.png'},
    {id: 2, imagePath: 'images/queen_of_diamonds2.png'},
    {id: 3, imagePath: 'images/jack_of_clubs2.png'},
    {id: 4, imagePath: 'images/ace_of_spades2.png'}
]

const cardBackImgPath = 'images/0_blue_back.png'
const cardContainerElem = document.querySelector('.card-container')

createCards()

function createCards(){
    cardObjectDefinition.forEach((cardItem) => {
        createCard(cardItem)
    })
}

function createCard(cardItem){
    // create div elements that make up a card
    const cardElem = createElement('div')
    const cardInnerElem = createElement('div')
    const cardFrontElem = createElement('div')
    const cardBackElem = createElement('div')

    // create front and back image eleents for a card
    const cardFrontImg = createElement('img')
    const cardBackImg = createElement('img')

    //  add class and id to card element
    addClassToElement(cardElem, 'card')
    addIdToElement(cardElem, cardItem.id)

    // add class to inner card element
    addClassToElement(cardInnerElem, 'card-inner')

    // add class to front card element
    addClassToElement(cardFrontElem, 'card-front')
    
    // add class to back card element
    addClassToElement(cardBackElem, 'card-back')

    // add src attribute and appropriate value to img element - back of card
    addSrcToImageElem(cardBackImg, cardBackImgPath)

    // add src attribute and appropriate value to img element - front of card
    addSrcToImageElem(cardFrontImg, cardItem.imagePath)

    // assign class to back image element of back of card
    addClassToElement(cardBackImg, 'card-img')

    // assign class to back image element of back of card
    addClassToElement(cardFrontImg, 'card-img')

    // add back image element as child element to back card element
    addChildElement(cardBackElem, cardBackImg)

    // add front image element as child element to front card element
    addChildElement(cardFrontElem, cardFrontImg)

    // add back card element as child element to inner card element
    addChildElement(cardInnerElem, cardBackElem)

    // add front card element as child element to inner card element
    addChildElement(cardInnerElem, cardFrontElem)

    // add inner card element as child element to card element
    addChildElement(cardElem, cardInnerElem)

    // add card element as child element to appropriate grid cell
    addCardToGridCell(cardElem)
}

function createElement(elemType){
    return document.createElement(elemType)
}

function addClassToElement(elem, className){
    elem.classList.add(className)
}

function addIdToElement(elem, id){
    elem.id = id
}

function addSrcToImageElem(imgElem, src){
    imgElem.src = src
}

function addChildElement(parentElem, childElem){
    parentElem.appendChild(childElem)
}

function addCardToGridCell(card){
    const cardPositionClassName = mapCardIdToGridCell(card)

    const cardPosElem = document.querySelector(cardPositionClassName)

    addChildElement(cardPosElem, card)
}

function mapCardIdToGridCell(card){
    if(card.id == 1){
        return '.card-pos-a'
    }
    if(card.id == 2){
        return '.card-pos-b'
    }
    if(card.id == 3){
        return '.card-pos-c'
    }
    if(card.id == 4){
        return '.card-pos-d'
    }
}
