
async function main() {
    const app = new PIXI.Application({
        view: document.getElementById('pio'),
        autoStart: true,
        resizeTo: window
    });

    const model = await PIXI.live2d.Live2DModel.from('https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json');

    app.stage.addChild(model);

    // transforms
    model.x = 100;
    model.y = 100;
    model.scale.set(0.2, 0.2);
    // model.rotation = Math.PI;
    // model.skew.x = Math.PI;
    // model.scale.set(2, 2);
    // model.anchor.set(0.5, 0.5);

    // interaction
    model.on('hit', hitAreas => {
        if (hitAreas.includes('body')) {
            model.motion('tap_body');
        }
    });
}

(main)()

//
// const cubism2Model =
//     "https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json";
// const cubism4Model =
//     "https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru_greeter_t03.model3.json";
//
// (async function main() {
//     const app = new PIXI.Application({
//         view: document.getElementById("live2d_display"),
//         autoStart: true,
//         resizeTo: window
//     });
//
//     const model2 = await PIXI.live2d.Live2DModel.from(cubism2Model);
//     const model4 = await PIXI.live2d.Live2DModel.from(cubism4Model);
//
//     app.stage.addChild(model2);
//     app.stage.addChild(model4);
//
//     model2.scale.set(0.3);
//     model4.scale.set(0.25);
//
//     model4.x = 300;
// })();
