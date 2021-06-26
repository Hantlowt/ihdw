<script>
	export let api;
	let categories_available = [];
	let cat_selected_available='';
	let categories_used = [];
	let cat_selected_used='';

	async function getCategories () { if (api) {
		categories_available = await api.getAvailableCategories()
		categories_used = await api.getUsedCategories()
		}
	}

	$: getCategories()
</script>

<aside>
	<h1>Add new pages</h1>
	Available categories : 
	<select bind:value={cat_selected_available}>
		{#each categories_available as cat}
			<option value={cat}>
				{cat}
			</option>
		{/each}
	</select>
	<button>Add</button>
</aside>

<aside>
	<h1>Pages</h1>
	Category : 
	<select bind:value={cat_selected_available}>
		{#each categories_used as cat}
			<option value={cat}>
				{cat}
			</option>
		{/each}
	</select>
</aside>