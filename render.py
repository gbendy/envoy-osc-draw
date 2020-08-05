render = {
	"resolution" : [ 1920, 1080 ],
	"frames": 5,
	"output": {
		"basename": "out_",
		"extname": "png",
		"width": 5,
		"format": "PNG"
	},
	"stills": {
		"background": {
			"background": "black"
		},
		"grids": {
			"lines" : [
				{
					"colour": [ 16, 84, 36, 255 ],
					"points": [ [ 0, 0 ], [ 0, 1 ], [ 1, 1 ], [ 1, 0 ] ],
					"width": "5px",
					"curve": True,
					"close": True
				}
			]
		},
		"grid2": {
			"lines" : [
				{
					"colour": "red",
					"points": [ [ 0, 0 ], [ "100px","50%" ] ],
					"width": "1.5px"					
				},
				{
					"colour": "red",
					"points": [ [ 1, 0 ], [ 0.2, 0.4 ] ],
					"width": "3px"				
				}
			],
		}
	},
	"anims": {
		"sinewaves": {
			"trigs": [
				{
					"method": "sin",
					"colour": [ 66, 255, 112 ],
					"start": [ 0, 0.5 ],
					"length": 1,
					"period": 1,
					"amplitude": 0.25,
					"offset": "frame_p * 100%",
					"width": "4px",
					"glow": True,
					"glow_scale": 0.6,
					"glow_color": [ 66, 219, 112 ]
				},
				{
					"method": "sin",
					"colour": [ 200, 255, 200 ],
					"start": [ 0, 0.5 ],
					"length": 1,
					"period": 1,
					"amplitude": 0.25,
					"offset": "frame_p * 100%",
					"width": "2px",
					"glow": False,
					"glow_scale": 0.6,
					"glow_color": [ 66, 219, 112 ]
				}
			],
			"_trigs": [
				{
					"method": "sin",
					"colour": [ 66, 219, 112 ],
					"start": [ 0, 0.5 ],
					"length": 1,
					"period": 1,
					"amplitude": 0.25,
					"offset": "frame_p * 100%",
					"width": "2px",
					"glow": True,
					"glow_scale": 0.6,
					"glow_color": [ 0, 255, 0 ]
				},
				{
					"method": "cos",
					"colour": [ 66, 219, 112 ],
					"start": [ 0, 0.5 ],
					"length": 1,
					"period": 1,
					"amplitude": "35% * math.sin(frame_p * 2 * 2 * math.pi)",
					"offset": "-frame_p * 100%",
					"width": "1.5px",
					"glow": True,
					"glow_scale": 0.4,
					"glow_color": [ 0, 255, 0 ]
				},
				{
					"method": "sin",
					"colour": [ 66, 219, 112 ],
					"start": [ 0, 0.5 ],
					"length": 1,
					"period": 0.05,
					"amplitude": "45% * math.sin(frame_p * 4 * 2 * math.pi)",
					"offset": "frame_p * 50%",
					"width": "2px",
					"glow": True,
					"glow_scale": 0.6,
					"glow_color": [ 0, 255, 0 ]
				}
			]
		}
	},
	"layers": [
		{
			"type": "still",
			"still": "background",
			"mode": "copy"
		},
		{
			"disable": True,
			"type": "still",
			"still": "grid2",
			"mode": "alpha"
		},
		{
			"disable": False,
			"type": "anim",
			"anim": "sinewaves",
			"mode": "alpha"
		},
		{
			"disable": True,
			"type": "still",
			"still": "grids",
			"mode": "alpha"
		}
	]
}