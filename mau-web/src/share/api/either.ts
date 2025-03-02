export type Either<L, R> = Left<L> | Right<R>

export interface Left<L> {
  type: 'left'
  value: L
}

export interface Right<R> {
  type: 'right'
  value: R
}

export function left<L>(value: L): Either<L, never> {
  return {
    type: 'left',
    value,
  }
}

export function right<R>(value: R): Either<never, R> {
  return {
    type: 'right',
    value,
  }
}
