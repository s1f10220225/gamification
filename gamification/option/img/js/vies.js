function displayRandomImage(category) {
    let randomList = [];
    
    if (category === 'fun') {
        randomList = [
            "../img/gamification/fun/3.png",
            "../img/gamification/fun/4.png",
            "../img/gamification/fun/5.png",
            "../img/gamification/fun/6.png",
            "../img/gamification/fun/7.png",
            "../img/gamification/fun/9.png",
            "../img/gamification/fun/10.png",
            "../img/gamification/fun/11.png",
            "../img/gamification/fun/16.png",
            "../img/gamification/fun/17.png",
            
        ];
    } else if (category === 'danger') {
        randomList = [
            "../img/gamification/danger/8.png",
            "../img/gamification/danger/12.png",
            "../img/gamification/danger/13.png",
            "../img/gamification/danger/14.png",
            "../img/gamification/danger/15.png"
        ];
    } else if (category === 'calm') {
        randomList = [
            "../img/gamification/calm/1.png",
            "../img/gamification/calm/2.png"
        ];
    }

    // ランダムな画像を選択
    var num = Math.floor(Math.random() * randomList.length);
    var selectedImage = randomList[num];

    // show.html に画像パスを渡して移動
    window.location.href = `show.html?image=${encodeURIComponent(selectedImage)}`;
}
