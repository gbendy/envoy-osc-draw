import math

from utils import animate_keyvals, animator_keyvals

background = {"background": [0,0,0,128]}
grids = {
	"lines": [
		{
			"colour": [16, 36, 84, 150],
			"points": [[x, 0], [x, 1]],
			"width": "2px",
			"curve": False,
			"close": False
		}
		for x in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
	] + [
		{
			"colour": [16, 36, 84, 150],
			"points": [[0, x], [1, x]],
			"width": "2px",
			"curve": False,
			"close": False
		}
		for x in [0.5, 0.67777, 0.32222, 0.8555, 0.1444 ]
	]
}

grid2 = {
	"lines": [
		{
			"colour": "red",
			"points": [[0, 0], ["100px", "50%"]],
			"width": "1.5px"
		},
		{
			"colour": "red",
			"points": [[1, 0], [0.2, 0.4]],
			"width": "3px"
		}
	],
}

def sine_callback(x, resolution, state, phase, period, amplitude):
	# period of 1.0 = 1 screen width
	period *= resolution[0]
	phase *= period
	# Amplitude of 1.0 = full screen height
	amplitude *= resolution[1]
	return math.sin(2 * math.pi * (x + phase) / period) * amplitude

sinewaves_new = {
	"functions": [
		{
			# "origin": [0, 0.5],
			"function": sine_callback,
			"parameters": {
				"period": 1,
				"phase": lambda state: state["frame_p"],
				"amplitude": 0.25,
			},
			"colour": [66, 255, 112],
			"width": "4px",
			"glow": True,
			"glow_scale": 9,
			"glow_color": [66, 219, 112]
		}
	]
}

def expanding_centre_throb_pts(state):
	delta = animate_keyvals((
		(0, 0.0),
		(1, 0.003),
		(5, 0.01),
		(20, 0.003),
		(40, 0.0)
	), state)
	return (
		(0.5 - delta, 0.499999),
		(0.5 - delta*2/5, 0.5-delta*2/5),
		(0.5, 0.5-delta/2),
		(0.5 + delta*2/5, 0.5-delta*2/5),
		(0.5 + delta, 0.5),
		(0.5 + delta*2/5, 0.5+delta*2/5),
		(0.5, 0.5 + delta / 2),
		(0.5 - delta*2/5, 0.5+delta*2/5),
		(0.5 - delta, 0.500001),
	)

def expanding_centre_throb_pts_flip(state):
	delta = animate_keyvals((
		(0, 0.0),
		(1, 0.003),
		(5, 0.01),
		(20, 0.003),
		(40, 0.0)
	), state)
	return (
		(0.5 + delta, 0.499999),
		(0.5 + delta*2/5, 0.5-delta*2/5),
		(0.5, 0.5-delta/2),
		(0.5 - delta*2/5, 0.5-delta*2/5),
		(0.5 - delta, 0.5),
		(0.5 - delta*2/5, 0.5+delta*2/5),
		(0.5, 0.5 + delta / 2),
		(0.5 + delta*2/5, 0.5+delta*2/5),
		(0.5 + delta, 0.500001),
	)

starting_throb = {
	"lines": [
		{
			"colour": [66, 255, 112],
			"width": animator_keyvals((
				(0, 1.0),
				(5, 30.0),
				(20, 1.0),
				(40, 1.0)
			)),
			"glow": True,
			"glow_scale": animator_keyvals((
				(0, 0.0),
				(5, 50.0),
				(20, 20.0),
				(40, 8.0)
			)),
			"glow_color": [66, 255, 112],
			"points": expanding_centre_throb_pts,
			"close": False,
		},
		{
			"colour": [66, 255, 112],
			"width": animator_keyvals((
				(0, 1.0),
				(5, 30.0),
				(20, 1.0),
				(40, 1.0)
			)),
			"glow": True,
			"glow_scale": animator_keyvals((
				(0, 0.0),
				(5, 50.0),
				(20, 20.0),
				(40, 8.0)
			)),
			"glow_color": [66, 255, 112],
			"points": expanding_centre_throb_pts_flip,
			"close": False,
		},
	],
}

def expanding_centre_pts(state):
	delta = animate_keyvals((
		(0, 0.0),
		(5, 0.01),
		(25, 0.5)
	), state)
	return (
		(0.5-delta, 0.5),
		(0.5+delta, 0.5),
	)

expanding_line = {
	"lines": [
		{
			"colour": [66, 255, 112],
			"width": 4.0,
			"glow": True,
			"glow_scale": 10.0,
			"glow_color": [66, 219, 112],
			"points": expanding_centre_pts,
			"close": False
		}
	]
}

sinewaves = {
	"trigs": [
		{
			"method": "sin",
			"colour": [66, 255, 112],
			"start": [0, 0.5],
			"length": 1,
			"period": 1,
			"amplitude": 0.25,
			"offset": "frame_p * 100%",
			"width": "4px",
			"glow": True,
			"glow_scale": 9,
			"glow_color": [66, 219, 112]
		},
		{
			"method": "sin",
			"colour": [200, 255, 200],
			"start": [0, 0.5],
			"length": 1,
			"period": 1,
			"amplitude": 0.25,
			"offset": "frame_p * 100%",
			"width": "2px",
			"glow": False,
			"glow_scale": 9,
			"glow_color": [66, 219, 112]
		}
	],
}

sinewaves2 = {
	"trigs": [
		{
			"method": "sin",
			"colour": [66, 219, 112],
			"start": [0, 0.5],
			"length": 1,
			"period": 1,
			"amplitude": 0.25,
			"offset": "frame_p * 100%",
			"width": "2px",
			"glow": True,
			"glow_scale": 9,
			"glow_color": [0, 255, 0]
		},
		{
			"method": "cos",
			"colour": [66, 219, 112],
			"start": [0, 0.5],
			"length": 1,
			"period": 1,
			"amplitude": "35% * math.sin(frame_p * 2 * 2 * math.pi)",
			"offset": "-frame_p * 100%",
			"width": "1.5px",
			"glow": True,
			"glow_scale": 9,
			"glow_color": [0, 255, 0]
		},
		{
			"method": "sin",
			"colour": [66, 219, 112],
			"start": [0, 0.5],
			"length": 1,
			"period": 0.05,
			"amplitude": "45% * math.sin(frame_p * 4 * 2 * math.pi)",
			"offset": "frame_p * 50%",
			"width": "2px",
			"glow": True,
			"glow_scale": 9,
			"glow_color": [0, 255, 0]
		}
	]
}

another_bit = {
	"resolution" : [ 1920, 1080 ],
	"frames": 50,
	"output": {
		"basename": "out_",
		"extname": "png",
		"width": 5,
		"format": "PNG"
	},
	"layers": [
		{
			"type": "still",
			"still": background,
			"mode": "copy"
		},
		{
			"disable": True,
			"type": "still",
			"still": grid2,
			"mode": "alpha"
		},
		{
			"disable": True,
			"type": "anim",
			"anim": sinewaves_new,
			"mode": "alpha"
		},
		{
			"type": "anim",
			"anim": starting_throb,
			"mode": "alpha"
		},
		{
			"type": "anim",
			"anim": expanding_line,
			"mode": "alpha"
		},
		{
			"disable": True,
			"type": "still",
			"still": grids,
			"mode": "alpha"
		}
	]
}

start_throb = {
	"resolution" : [ 1920, 1080 ],
	"frames": 50,
	"output": {
		"basename": "out_",
		"extname": "png",
		"width": 5,
		"format": "PNG"
	},
	"layers": [
		{
			"type": "still",
			"still": background,
			"mode": "copy"
		},
		{
			"type": "anim",
			"anim": starting_throb,
			"mode": "alpha"
		},
		{
			"type": "anim",
			"anim": expanding_line,
			"mode": "alpha"
		}
	]
}

render = start_throb