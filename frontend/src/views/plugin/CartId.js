// import React from 'react'

// const CartId = () => {
//     const generateRandomString = () => {
//         const length = 6;
//         const characters = "1234567890";
//         let randomString = "";
        
//         for(let i = 0; i < length; i++) {
//             const randomIndex = Math.floor(Math.random() * characters.length);
//             randomString += characters.charAt(randomIndex);
//         }
//         localStorage.setItem('randomString',randomString);

//     };
//     const existingRandomString = localStorage.getItem("randomString");
//     if(!existingRandomString) {
//         generateRandomString();
//     }
//    return existingRandomString;
// }

// export default CartId



const CartId = () => {
    let existingRandomString = localStorage.getItem("randomString");
    if (!existingRandomString) {
      const length = 6;
      const characters = "1234567890";
      let randomString = "";
      for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        randomString += characters.charAt(randomIndex);
      }
      localStorage.setItem("randomString", randomString);
      existingRandomString = randomString;  // Set it after generation
    }
    return existingRandomString;
  };
  
  export default CartId;