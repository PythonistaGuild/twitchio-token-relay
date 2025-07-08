import createEmblaCarousel from "embla-carousel-solid";
import ChevronBack from "../assets/chevron-back.svg";
import ChevronForward from "../assets/chevron-forward.svg";
import type { ParentProps } from "../types/components";

createEmblaCarousel.globalOptions = { loop: true };

function Carousel(props: ParentProps) {
	createEmblaCarousel.globalOptions = { loop: true }
	const [emblaRef, emblaApi] = createEmblaCarousel();

	const next = () => {
		const api = emblaApi();
		if (api) api.scrollNext();
	};

	const prev = () => {
		const api = emblaApi();
		if (api) api.scrollPrev();
	};

	return (
		<div class="embla">
			<div class="embla__viewport" ref={emblaRef}>
				<div class="embla__container">{props.children}</div>
			</div>
			<div class="sliderButtons">
				<button class="embla__prev sliderButton leftButton" onClick={prev}>
					<img src={ChevronBack} />
				</button>
				<button class="embla__next sliderButton rightButton" onClick={next}>
					<img src={ChevronForward} />
				</button>
			</div>
		</div>
	);
}

export default Carousel;
