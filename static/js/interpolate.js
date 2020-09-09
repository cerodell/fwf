/*
RainbowVis-JS 
Released under Eclipse Public License - v 1.0
*/
var color_map_qpf_3h = {};

    
color_map_qpf_3h.color = d3.scale.threshold()
		  .domain([0.0, 0.280561122244489, 0.561122244488978, 0.8416833667334669, 1.122244488977956, 1.402805611222445, 1.6833667334669338, 1.9639278557114228, 2.244488977955912, 2.5250501002004007, 2.80561122244489, 3.0861723446893787, 3.3667334669338675, 3.647294589178357, 3.9278557114228456, 4.208416833667335, 4.488977955911824, 4.7695390781563125, 5.050100200400801, 5.330661322645291, 5.61122244488978, 5.891783567134269, 6.1723446893787575, 6.452905811623246, 6.733466933867735, 7.014028056112225, 7.294589178356714, 7.575150300601202, 7.855711422845691, 8.136272545090181, 8.41683366733467, 8.697394789579159, 8.977955911823647, 9.258517034068136, 9.539078156312625, 9.819639278557114, 10.100200400801603, 10.380761523046091, 10.661322645290582, 10.94188376753507, 11.22244488977956, 11.503006012024048, 11.783567134268537, 12.064128256513026, 12.344689378757515, 12.625250501002004, 12.905811623246493, 13.186372745490981, 13.46693386773547, 13.74749498997996, 14.02805611222445, 14.308617234468938, 14.589178356713427, 14.869739478957916, 15.150300601202405, 15.430861723446894, 15.711422845691382, 15.991983967935871, 16.272545090180362, 16.55310621242485, 16.83366733466934, 17.11422845691383, 17.394789579158317, 17.675350701402806, 17.955911823647295, 18.236472945891784, 18.517034068136272, 18.79759519038076, 19.07815631262525, 19.35871743486974, 19.639278557114228, 19.919839679358716, 20.200400801603205, 20.480961923847694, 20.761523046092183, 21.04208416833667, 21.322645290581164, 21.603206412825653, 21.88376753507014, 22.16432865731463, 22.44488977955912, 22.725450901803608, 23.006012024048097, 23.286573146292586, 23.567134268537075, 23.847695390781563, 24.128256513026052, 24.40881763527054, 24.68937875751503, 24.96993987975952, 25.250501002004007, 25.531062124248496, 25.811623246492985, 26.092184368737474, 26.372745490981963, 26.65330661322645, 26.93386773547094, 27.21442885771543, 27.49498997995992, 27.77555110220441, 28.0561122244489, 28.336673346693388, 28.617234468937877, 28.897795591182366, 29.178356713426854, 29.458917835671343, 29.739478957915832, 30.02004008016032, 30.30060120240481, 30.5811623246493, 30.861723446893787, 31.142284569138276, 31.422845691382765, 31.703406813627254, 31.983967935871743, 32.26452905811623, 32.545090180360724, 32.82565130260521, 33.1062124248497, 33.38677354709419, 33.66733466933868, 33.947895791583164, 34.22845691382766, 34.50901803607214, 34.789579158316634, 35.07014028056112, 35.35070140280561, 35.6312625250501, 35.91182364729459, 36.192384769539075, 36.47294589178357, 36.75350701402806, 37.034068136272545, 37.31462925851704, 37.59519038076152, 37.875751503006015, 38.1563126252505, 38.43687374749499, 38.71743486973948, 38.99799599198397, 39.278557114228455, 39.55911823647295, 39.83967935871743, 40.120240480961925, 40.40080160320641, 40.6813627254509, 40.96192384769539, 41.24248496993988, 41.523046092184366, 41.80360721442886, 42.08416833667334, 42.364729458917836, 42.64529058116233, 42.92585170340681, 43.206412825651306, 43.48697394789579, 43.76753507014028, 44.04809619238477, 44.32865731462926, 44.609218436873746, 44.88977955911824, 45.170340681362724, 45.450901803607216, 45.7314629258517, 46.012024048096194, 46.29258517034068, 46.57314629258517, 46.85370741482966, 47.13426853707415, 47.414829659318634, 47.69539078156313, 47.97595190380761, 48.256513026052104, 48.53707414829659, 48.81763527054108, 49.098196392785574, 49.37875751503006, 49.65931863727455, 49.93987975951904, 50.22044088176353, 50.501002004008015, 50.78156312625251, 51.06212424849699, 51.342685370741485, 51.62324649298597, 51.90380761523046, 52.18436873747495, 52.46492985971944, 52.745490981963925, 53.02605210420842, 53.3066132264529, 53.587174348697395, 53.86773547094188, 54.14829659318637, 54.42885771543086, 54.70941883767535, 54.98997995991984, 55.27054108216433, 55.55110220440882, 55.831663326653306, 56.1122244488978, 56.392785571142284, 56.673346693386776, 56.95390781563126, 57.234468937875754, 57.51503006012024, 57.79559118236473, 58.07615230460922, 58.35671342685371, 58.637274549098194, 58.91783567134269, 59.19839679358717, 59.478957915831664, 59.75951903807615, 60.04008016032064, 60.32064128256513, 60.60120240480962, 60.88176352705411, 61.1623246492986, 61.44288577154309, 61.723446893787575, 62.00400801603207, 62.28456913827655, 62.565130260521045, 62.84569138276553, 63.12625250501002, 63.40681362725451, 63.687374749499, 63.967935871743485, 64.24849699398797, 64.52905811623246, 64.80961923847696, 65.09018036072145, 65.37074148296593, 65.65130260521042, 65.93186372745491, 66.2124248496994, 66.49298597194388, 66.77354709418837, 67.05410821643287, 67.33466933867736, 67.61523046092185, 67.89579158316633, 68.17635270541082, 68.45691382765531, 68.7374749498998, 69.01803607214428, 69.29859719438878, 69.57915831663327, 69.85971943887776, 70.14028056112224, 70.42084168336673, 70.70140280561122, 70.98196392785572, 71.2625250501002, 71.54308617234469, 71.82364729458918, 72.10420841683367, 72.38476953907815, 72.66533066132264, 72.94589178356713, 73.22645290581163, 73.50701402805612, 73.7875751503006, 74.06813627254509, 74.34869739478958, 74.62925851703407, 74.90981963927855, 75.19038076152304, 75.47094188376754, 75.75150300601203, 76.03206412825651, 76.312625250501, 76.59318637274549, 76.87374749498998, 77.15430861723446, 77.43486973947896, 77.71543086172345, 77.99599198396794, 78.27655310621242, 78.55711422845691, 78.8376753507014, 79.1182364729459, 79.39879759519039, 79.67935871743487, 79.95991983967936, 80.24048096192385, 80.52104208416834, 80.80160320641282, 81.08216432865731, 81.3627254509018, 81.6432865731463, 81.92384769539078, 82.20440881763527, 82.48496993987976, 82.76553106212425, 83.04609218436873, 83.32665330661322, 83.60721442885772, 83.88777555110221, 84.16833667334669, 84.44889779559118, 84.72945891783567, 85.01002004008016, 85.29058116232466, 85.57114228456913, 85.85170340681363, 86.13226452905812, 86.41282565130261, 86.69338677354709, 86.97394789579158, 87.25450901803607, 87.53507014028057, 87.81563126252505, 88.09619238476954, 88.37675350701403, 88.65731462925852, 88.937875751503, 89.21843687374749, 89.49899799599199, 89.77955911823648, 90.06012024048096, 90.34068136272545, 90.62124248496994, 90.90180360721443, 91.18236472945891, 91.4629258517034, 91.7434869739479, 92.02404809619239, 92.30460921843688, 92.58517034068136, 92.86573146292585, 93.14629258517034, 93.42685370741484, 93.70741482965931, 93.9879759519038, 94.2685370741483, 94.54909819639279, 94.82965931863727, 95.11022044088176, 95.39078156312625, 95.67134268537075, 95.95190380761522, 96.23246492985972, 96.51302605210421, 96.7935871743487, 97.07414829659318, 97.35470941883767, 97.63527054108216, 97.91583166332666, 98.19639278557115, 98.47695390781563, 98.75751503006012, 99.03807615230461, 99.3186372745491, 99.59919839679358, 99.87975951903807, 100.16032064128257, 100.44088176352706, 100.72144288577154, 101.00200400801603, 101.28256513026052, 101.56312625250501, 101.84368737474949, 102.12424849699399, 102.40480961923848, 102.68537074148297, 102.96593186372745, 103.24649298597194, 103.52705410821643, 103.80761523046093, 104.08817635270542, 104.3687374749499, 104.64929859719439, 104.92985971943888, 105.21042084168337, 105.49098196392785, 105.77154308617234, 106.05210420841684, 106.33266533066133, 106.6132264529058, 106.8937875751503, 107.17434869739479, 107.45490981963928, 107.73547094188376, 108.01603206412825, 108.29659318637275, 108.57715430861724, 108.85771543086172, 109.13827655310621, 109.4188376753507, 109.6993987975952, 109.97995991983969, 110.26052104208416, 110.54108216432866, 110.82164328657315, 111.10220440881764, 111.38276553106212, 111.66332665330661, 111.9438877755511, 112.2244488977956, 112.50501002004007, 112.78557114228457, 113.06613226452906, 113.34669338677355, 113.62725450901803, 113.90781563126252, 114.18837675350701, 114.46893787575151, 114.74949899799599, 115.03006012024048, 115.31062124248497, 115.59118236472946, 115.87174348697395, 116.15230460921843, 116.43286573146293, 116.71342685370742, 116.99398797595191, 117.27454909819639, 117.55511022044088, 117.83567134268537, 118.11623246492987, 118.39679358717434, 118.67735470941884, 118.95791583166333, 119.23847695390782, 119.5190380761523, 119.79959919839679, 120.08016032064128, 120.36072144288578, 120.64128256513025, 120.92184368737475, 121.20240480961924, 121.48296593186373, 121.76352705410822, 122.0440881763527, 122.3246492985972, 122.60521042084169, 122.88577154308618, 123.16633266533066, 123.44689378757515, 123.72745490981964, 124.00801603206413, 124.28857715430861, 124.5691382765531, 124.8496993987976, 125.13026052104209, 125.41082164328657, 125.69138276553106, 125.97194388777555, 126.25250501002004, 126.53306613226452, 126.81362725450902, 127.09418837675351, 127.374749498998, 127.65531062124248, 127.93587174348697, 128.21643286573146, 128.49699398797594, 128.77755511022045, 129.05811623246493, 129.33867735470943, 129.6192384769539, 129.8997995991984, 130.1803607214429, 130.46092184368737, 130.74148296593185, 131.02204408817636, 131.30260521042084, 131.58316633266534, 131.86372745490982, 132.1442885771543, 132.4248496993988, 132.70541082164328, 132.98597194388776, 133.26653306613227, 133.54709418837675, 133.82765531062125, 134.10821643286573, 134.3887775551102, 134.66933867735472, 134.9498997995992, 135.2304609218437, 135.51102204408818, 135.79158316633266, 136.07214428857716, 136.35270541082164, 136.63326653306612, 136.91382765531063, 137.1943887775551, 137.4749498997996, 137.7555110220441, 138.03607214428857, 138.31663326653307, 138.59719438877755, 138.87775551102203, 139.15831663326654, 139.43887775551102, 139.71943887775552, 140.0])
		  .range(['#ffffffff', '#ffffffff', '#a9a5a5ff', '#a9a5a5ff', '#6e6e6eff', '#6e6e6eff', '#6e6e6eff', '#6e6e6eff', '#b3f9a9ff', '#b3f9a9ff', '#b3f9a9ff', '#79f572ff', '#79f572ff', '#79f572ff', '#79f572ff', '#79f572ff', '#79f572ff', '#79f572ff', '#79f572ff', '#79f572ff', '#79f572ff', '#79f572ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#50f150ff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#1fb51eff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#0ca10dff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#1563d3ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#54a8f5ff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#b4f1fbff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffe978ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ffa100ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#ff3300ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#a50000ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#b58d83ff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#9886baff', '#8d008dff']);


color_map_qpf_3h.x = d3.scale.linear()
		  .domain([0.0, 140.0])
		  .range([0, 400]);

color_map_qpf_3h.legend = L.control({position: 'bottomright'});
color_map_qpf_3h.legend.onAdd = function (map) {var div = L.DomUtil.create('div', 'legend'); return div};
color_map_qpf_3h.legend.addTo(map);

color_map_qpf_3h.xAxis = d3.svg.axis()
	.scale(color_map_qpf_3h.x)
	.orient("top")
	.tickSize(1)
	.tickValues([0, '', 1, '', 3, '', 10, '', 20, '', 30, '', 50, '', 70, '', 100, '']);

color_map_qpf_3h.svg = d3.select(".legend.leaflet-control").append("svg")
	.attr("id", 'legend')
	.attr("width", 450)
	.attr("height", 40);

color_map_qpf_3h.g = color_map_qpf_3h.svg.append("g")
	.attr("class", "key")
	.attr("transform", "translate(25,16)");

color_map_qpf_3h.g.selectAll("rect")
	.data(color_map_qpf_3h.color.range().map(function(d, i) {
	  return {
		x0: i ? color_map_qpf_3h.x(color_map_qpf_3h.color.domain()[i - 1]) : color_map_qpf_3h.x.range()[0],
		x1: i < color_map_qpf_3h.color.domain().length ? color_map_qpf_3h.x(color_map_qpf_3h.color.domain()[i]) : color_map_qpf_3h.x.range()[1],
		z: d
	  };
	}))
  .enter().append("rect")
	.attr("height", 10)
	.attr("x", function(d) { return d.x0; })
	.attr("width", function(d) { return d.x1 - d.x0; })
	.style("fill", function(d) { return d.z; });

color_map_qpf_3h.g.call(color_map_qpf_3h.xAxis).append("text")
	.attr("class", "caption")
	.attr("y", 21)
	.text('Total Accumulated Precipitation (mm)');



function Rainbow()
{
	"use strict";
	var gradients = null;
	var minNum = 0;
	var maxNum = 100;
	var colours = ['ff0000', 'ffff00', '00ff00', '0000ff']; 
	setColours(colours);
	
	function setColours (spectrum) 
	{
		if (spectrum.length < 2) {
			throw new Error('Rainbow must have two or more colours.');
		} else {
			var increment = (maxNum - minNum)/(spectrum.length - 1);
			var firstGradient = new ColourGradient();
			firstGradient.setGradient(spectrum[0], spectrum[1]);
			firstGradient.setNumberRange(minNum, minNum + increment);
			gradients = [ firstGradient ];
			
			for (var i = 1; i < spectrum.length - 1; i++) {
				var colourGradient = new ColourGradient();
				colourGradient.setGradient(spectrum[i], spectrum[i + 1]);
				colourGradient.setNumberRange(minNum + increment * i, minNum + increment * (i + 1)); 
				gradients[i] = colourGradient; 
			}

			colours = spectrum;
		}
	}

	this.setSpectrum = function () 
	{
		setColours(arguments);
		return this;
	}

	this.setSpectrumByArray = function (array)
	{
		setColours(array);
		return this;
	}

	this.colourAt = function (number)
	{
		if (isNaN(number)) {
			throw new TypeError(number + ' is not a number');
		} else if (gradients.length === 1) {
			return gradients[0].colourAt(number);
		} else {
			var segment = (maxNum - minNum)/(gradients.length);
			var index = Math.min(Math.floor((Math.max(number, minNum) - minNum)/segment), gradients.length - 1);
			return gradients[index].colourAt(number);
		}
	}

	this.colorAt = this.colourAt;

	this.setNumberRange = function (minNumber, maxNumber)
	{
		if (maxNumber > minNumber) {
			minNum = minNumber;
			maxNum = maxNumber;
			setColours(colours);
		} else {
			throw new RangeError('maxNumber (' + maxNumber + ') is not greater than minNumber (' + minNumber + ')');
		}
		return this;
	}
}

function ColourGradient() 
{
	"use strict";
	var startColour = 'ff0000';
	var endColour = '0000ff';
	var minNum = 0;
	var maxNum = 100;

	this.setGradient = function (colourStart, colourEnd)
	{
		startColour = getHexColour(colourStart);
		endColour = getHexColour(colourEnd);
	}

	this.setNumberRange = function (minNumber, maxNumber)
	{
		if (maxNumber > minNumber) {
			minNum = minNumber;
			maxNum = maxNumber;
		} else {
			throw new RangeError('maxNumber (' + maxNumber + ') is not greater than minNumber (' + minNumber + ')');
		}
	}

	this.colourAt = function (number)
	{
		return calcHex(number, startColour.substring(0,2), endColour.substring(0,2)) 
			+ calcHex(number, startColour.substring(2,4), endColour.substring(2,4)) 
			+ calcHex(number, startColour.substring(4,6), endColour.substring(4,6));
	}
	
	function calcHex(number, channelStart_Base16, channelEnd_Base16)
	{
		var num = number;
		if (num < minNum) {
			num = minNum;
		}
		if (num > maxNum) {
			num = maxNum;
		} 
		var numRange = maxNum - minNum;
		var cStart_Base10 = parseInt(channelStart_Base16, 16);
		var cEnd_Base10 = parseInt(channelEnd_Base16, 16); 
		var cPerUnit = (cEnd_Base10 - cStart_Base10)/numRange;
		var c_Base10 = Math.round(cPerUnit * (num - minNum) + cStart_Base10);
		return formatHex(c_Base10.toString(16));
	}

	function formatHex(hex) 
	{
		if (hex.length === 1) {
			return '0' + hex;
		} else {
			return hex;
		}
	} 
	
	function isHexColour(string)
	{
		var regex = /^#?[0-9a-fA-F]{6}$/i;
		return regex.test(string);
	}

	function getHexColour(string)
	{
		if (isHexColour(string)) {
			return string.substring(string.length - 6, string.length);
		} else {
			var name = string.toLowerCase();
			if (colourNames.hasOwnProperty(name)) {
				return colourNames[name];
			}
			throw new Error(string + ' is not a valid colour.');
		}
	}
	
	// Extended list of CSS colornames s taken from
	// http://www.w3.org/TR/css3-color/#svg-color
	var colourNames = {
		aliceblue: "F0F8FF",
		antiquewhite: "FAEBD7",
		aqua: "00FFFF",
		aquamarine: "7FFFD4",
		azure: "F0FFFF",
		beige: "F5F5DC",
		bisque: "FFE4C4",
		black: "000000",
		blanchedalmond: "FFEBCD",
		blue: "0000FF",
		blueviolet: "8A2BE2",
		brown: "A52A2A",
		burlywood: "DEB887",
		cadetblue: "5F9EA0",
		chartreuse: "7FFF00",
		chocolate: "D2691E",
		coral: "FF7F50",
		cornflowerblue: "6495ED",
		cornsilk: "FFF8DC",
		crimson: "DC143C",
		cyan: "00FFFF",
		darkblue: "00008B",
		darkcyan: "008B8B",
		darkgoldenrod: "B8860B",
		darkgray: "A9A9A9",
		darkgreen: "006400",
		darkgrey: "A9A9A9",
		darkkhaki: "BDB76B",
		darkmagenta: "8B008B",
		darkolivegreen: "556B2F",
		darkorange: "FF8C00",
		darkorchid: "9932CC",
		darkred: "8B0000",
		darksalmon: "E9967A",
		darkseagreen: "8FBC8F",
		darkslateblue: "483D8B",
		darkslategray: "2F4F4F",
		darkslategrey: "2F4F4F",
		darkturquoise: "00CED1",
		darkviolet: "9400D3",
		deeppink: "FF1493",
		deepskyblue: "00BFFF",
		dimgray: "696969",
		dimgrey: "696969",
		dodgerblue: "1E90FF",
		firebrick: "B22222",
		floralwhite: "FFFAF0",
		forestgreen: "228B22",
		fuchsia: "FF00FF",
		gainsboro: "DCDCDC",
		ghostwhite: "F8F8FF",
		gold: "FFD700",
		goldenrod: "DAA520",
		gray: "808080",
		green: "008000",
		greenyellow: "ADFF2F",
		grey: "808080",
		honeydew: "F0FFF0",
		hotpink: "FF69B4",
		indianred: "CD5C5C",
		indigo: "4B0082",
		ivory: "FFFFF0",
		khaki: "F0E68C",
		lavender: "E6E6FA",
		lavenderblush: "FFF0F5",
		lawngreen: "7CFC00",
		lemonchiffon: "FFFACD",
		lightblue: "ADD8E6",
		lightcoral: "F08080",
		lightcyan: "E0FFFF",
		lightgoldenrodyellow: "FAFAD2",
		lightgray: "D3D3D3",
		lightgreen: "90EE90",
		lightgrey: "D3D3D3",
		lightpink: "FFB6C1",
		lightsalmon: "FFA07A",
		lightseagreen: "20B2AA",
		lightskyblue: "87CEFA",
		lightslategray: "778899",
		lightslategrey: "778899",
		lightsteelblue: "B0C4DE",
		lightyellow: "FFFFE0",
		lime: "00FF00",
		limegreen: "32CD32",
		linen: "FAF0E6",
		magenta: "FF00FF",
		maroon: "800000",
		mediumaquamarine: "66CDAA",
		mediumblue: "0000CD",
		mediumorchid: "BA55D3",
		mediumpurple: "9370DB",
		mediumseagreen: "3CB371",
		mediumslateblue: "7B68EE",
		mediumspringgreen: "00FA9A",
		mediumturquoise: "48D1CC",
		mediumvioletred: "C71585",
		midnightblue: "191970",
		mintcream: "F5FFFA",
		mistyrose: "FFE4E1",
		moccasin: "FFE4B5",
		navajowhite: "FFDEAD",
		navy: "000080",
		oldlace: "FDF5E6",
		olive: "808000",
		olivedrab: "6B8E23",
		orange: "FFA500",
		orangered: "FF4500",
		orchid: "DA70D6",
		palegoldenrod: "EEE8AA",
		palegreen: "98FB98",
		paleturquoise: "AFEEEE",
		palevioletred: "DB7093",
		papayawhip: "FFEFD5",
		peachpuff: "FFDAB9",
		peru: "CD853F",
		pink: "FFC0CB",
		plum: "DDA0DD",
		powderblue: "B0E0E6",
		purple: "800080",
		red: "FF0000",
		rosybrown: "BC8F8F",
		royalblue: "4169E1",
		saddlebrown: "8B4513",
		salmon: "FA8072",
		sandybrown: "F4A460",
		seagreen: "2E8B57",
		seashell: "FFF5EE",
		sienna: "A0522D",
		silver: "C0C0C0",
		skyblue: "87CEEB",
		slateblue: "6A5ACD",
		slategray: "708090",
		slategrey: "708090",
		snow: "FFFAFA",
		springgreen: "00FF7F",
		steelblue: "4682B4",
		tan: "D2B48C",
		teal: "008080",
		thistle: "D8BFD8",
		tomato: "FF6347",
		turquoise: "40E0D0",
		violet: "EE82EE",
		wheat: "F5DEB3",
		white: "FFFFFF",
		whitesmoke: "F5F5F5",
		yellow: "FFFF00",
		yellowgreen: "9ACD32"
	}
}

if (typeof module !== 'undefined') {
  module.exports = Rainbow;
}