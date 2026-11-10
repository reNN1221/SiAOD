#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def less(x, y):
    """Сравнение ключей: для пар (ключ, метка) сравниваем только ключ."""
    if isinstance(x, tuple) and isinstance(y, tuple):
        return x[0] < y[0]
    return x < y


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Пузырёк: лучший случай O(n), средний и худший O(n^2). Возвращает копию, сравнения, обмены."""
    a = list(a)
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comparisons += 1
            if less(a[j + 1], a[j]):
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return a, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Вставки: лучший случай O(n), средний и худший O(n^2); перемещения — сдвиги."""
    a = list(a)
    comparisons = 0
    shifts = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and less(key, a[j]):
            comparisons += 1
            a[j + 1] = a[j]
            shifts += 1
            j -= 1
        if j >= 0:
            comparisons += 1
        a[j + 1] = key
    return a, comparisons, shifts


def selection_sort(a: list) -> tuple[list, int, int]:
    """Выбор: Θ(n^2) сравнений при любом порядке; обмены — только если минимум не на месте."""
    a = list(a)
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if less(a[j], a[min_idx]):
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            swaps += 1
    return a, comparisons, swaps

# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """Рандомизированный QuickSort: среднее O(n log n), худшее O(n^2); вход не изменяется."""
    if rng is None:
        rng = random.Random()
    a = list(a)

    def partition(lo: int, hi: int) -> int:
        k = rng.randrange(lo, hi + 1) 
        a[k], a[hi] = a[hi], a[k] 
        p = a[hi] 
        i = lo 
        for j in range(lo, hi):
            if less(a[j], p):
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i] 
        return i 

    def sort(lo: int, hi: int) -> None:
        if lo >= hi: 
            return
        m = partition(lo, hi)
        sort(lo, m - 1)
        sort(m + 1, hi)

    sort(0, len(a) - 1)
    return a

# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показывает сохранение/изменение порядка меток при равных ключах."""
    pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d"), (2, "e"), (1, "f")]
    # Стабильность проверяется только по ключу, а не по всей паре.
    algorithms = {
        "bubble_sort": lambda x: bubble_sort(x)[0],
        "insertion_sort": lambda x: insertion_sort(x)[0],
        "selection_sort": lambda x: selection_sort(x)[0],
        "quick_sort": lambda x: quick_sort(x, random.Random(7)),
    }
    print("\nДемонстрация стабильности (ключ, метка):")
    print("  исходный:", pairs)
    for name, fn in algorithms.items():
        result = fn(pairs)
        stable = True
        for key in {p[0] for p in pairs}:
            before = [p[1] for p in pairs if p[0] == key]
            after = [p[1] for p in result if p[0] == key]
            if before != after:
                stable = False
        print(f"  {name:<16} {result} — {'стабильная на этом примере' if stable else 'нестабильная на этом примере'}")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(not less(a[i + 1], a[i]) for i in range(len(a) - 1))


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def check_algorithm(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(is_sorted(res), f"нарушен порядок на {a}: получено {res}")
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        res = fn(list(a))
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_counters() -> None:
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    expect(comparisons == 10, f"selection_sort: {comparisons} сравнений вместо 10")
    _, comparisons, swaps = bubble_sort([1, 2, 3])
    expect(comparisons == 2 and swaps == 0, "пузырёк должен завершиться за один проход на отсортированном массиве")
    _, comparisons, _ = insertion_sort([1, 2, 3])
    expect(comparisons == 2, "вставки на упорядоченном массиве должны сделать n-1 сравнений")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_algorithm(fn)) for name, fn in ALGORITHMS.items()]
    checks.append(("счётчики", check_counters))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    # TODO: добавить собственные проверки (стабильность, счётчики пузырька и вставок)
    #       и описать их в отчёте.
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int, out_dir: Path) -> None:
    """Замеры, наклоны, log-log графики и таблица счётчиков."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as err:
        raise SystemExit("Не найден matplotlib. Выполни: pip install matplotlib") from err

    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]

    # 1. Замеры
    records = {}
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        records[name] = {"упорядоченный": [], "случайный": [], "обратный": []}
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                records[name][cls].append((n, t))
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")

    # 2. Наклоны
    print("\nНаклоны log-log (по первой и последней точке):")
    for name, by_cls in records.items():
        for cls, pts in by_cls.items():
            (n1, t1), (n2, t2) = pts[0], pts[-1]
            k = math.log(t2 / t1) / math.log(n2 / n1)
            print(f"  {name:<15} {cls:<13} k = {k:.2f}")

    # 3. Графики
    for name, by_cls in records.items():
        fig, ax = plt.subplots()
        for cls, pts in by_cls.items():
            ax.loglog([p[0] for p in pts], [p[1] for p in pts], marker="o", label=cls)
        ax.set_title(f"{name}: время от размера входа")
        ax.set_xlabel("n (log)")
        ax.set_ylabel("медиана времени, с (log)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        path = out_dir / f"lab03_{name}.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"График сохранён: {path}")

    # 4. Таблица счётчиков
    print("\nСчётчики, n = 1000 (сравнения / обмены или сдвиги):")
    for cls, data in make_inputs(1000, seed).items():
        print(f"  вход: {cls}")
        for name, fn in [("bubble_sort", bubble_sort),
                         ("insertion_sort", insertion_sort),
                         ("selection_sort", selection_sort)]:
            _, c, m = fn(data)
            print(f"    {name:<15} {c:>8} / {m:>8}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", default=None, help="папка для графиков (по умолчанию рядом со скриптом)")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    out_dir = Path(args.out).resolve() if args.out else Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Вариант {args.variant}; seed={seed}")
    self_check()
    stability_demo()
    run_benchmarks(seed, out_dir)


if __name__ == "__main__":
    main()
